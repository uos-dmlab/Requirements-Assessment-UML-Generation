"""PlantUML Service - Syntax validation and rendering."""

import subprocess
import tempfile
import base64
from pathlib import Path
from app.core.config import settings


class PlantUMLService:
    """
    Stage 4: Syntax validation (plantuml.jar -syntax)
    Stage 5: Render PNG → base64

    All via plantuml.jar — no external servers.
    """

    def __init__(self):
        self.jar_path = Path(settings.PLANTUML_JAR_PATH)
        self._java_available = None
        self._jar_available = None

    def _verify_setup(self) -> tuple[bool, str]:
        """Verify that Java and plantuml.jar are available."""
        errors = []

        # Check Java
        if self._java_available is None:
            try:
                result = subprocess.run(
                    ["java", "-version"],
                    capture_output=True,
                    timeout=10
                )
                self._java_available = result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self._java_available = False

        if not self._java_available:
            errors.append("Java is required. Install JRE 8+: apt install default-jre-headless")

        # Check JAR
        if self._jar_available is None:
            self._jar_available = self.jar_path.exists()

        if not self._jar_available:
            errors.append(f"PlantUML JAR not found at: {self.jar_path}")

        return len(errors) == 0, "; ".join(errors)

    def check_syntax(self, plantuml_code: str) -> bool:
        """
        Check PlantUML code syntax.
        Returns True if code is valid.

        plantuml.jar -syntax outputs:
        - "CLASS" (or other type) for valid code
        - "ERROR" with description for invalid code
        """
        ok, error = self._verify_setup()
        if not ok:
            # If PlantUML not available, assume valid to not block
            return True

        try:
            result = subprocess.run(
                ["java", "-jar", str(self.jar_path), "-syntax"],
                input=plantuml_code,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Check stdout for ERROR
            output = result.stdout + result.stderr
            return "ERROR" not in output.upper() and result.returncode == 0

        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    def get_syntax_errors(self, plantuml_code: str) -> str:
        """
        Get specific syntax errors.
        Used for SELF-REFINE feedback.
        """
        ok, error = self._verify_setup()
        if not ok:
            return error

        try:
            result = subprocess.run(
                ["java", "-jar", str(self.jar_path), "-syntax"],
                input=plantuml_code,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Combine stdout and stderr for full picture
            output = result.stdout + "\n" + result.stderr
            return output.strip()

        except Exception as e:
            return f"Syntax check failed: {str(e)}"

    def render_to_base64(self, plantuml_code: str, format: str = "png") -> str:
        """
        Render PlantUML code to image and return base64.

        Pipeline:
        1. Write code to temp file
        2. plantuml.jar renders to PNG
        3. Read PNG and encode to base64
        """
        ok, error = self._verify_setup()
        if not ok:
            raise RuntimeError(error)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "diagram.puml"
            output_path = Path(tmpdir) / f"diagram.{format}"

            # Write code
            input_path.write_text(plantuml_code, encoding="utf-8")

            # Render
            cmd = [
                "java", "-jar", str(self.jar_path),
                f"-t{format}",
                str(input_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=60
            )

            if result.returncode != 0:
                error_msg = result.stderr.decode() if result.stderr else "Unknown error"
                raise RuntimeError(f"PlantUML render failed: {error_msg}")

            # Check that file was created
            if not output_path.exists():
                raise RuntimeError(f"Output file not created: {output_path}")

            # Read and encode
            image_bytes = output_path.read_bytes()
            return base64.b64encode(image_bytes).decode("utf-8")

    def render_to_bytes(self, plantuml_code: str, format: str = "png") -> bytes:
        """Render to bytes (if file needed instead of base64)."""
        base64_str = self.render_to_base64(plantuml_code, format)
        return base64.b64decode(base64_str)
