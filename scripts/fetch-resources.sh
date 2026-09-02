#!/usr/bin/env bash
# Fetch third-party resources that are not redistributed in this repository:
#   - plantuml.jar          : renders and syntax-checks generated PlantUML
#   - the Language Reference Guide : corpus indexed by the RAG vector store
#
# Both carry their own licenses and are therefore downloaded rather than committed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RES="$ROOT/backend/resources"
mkdir -p "$RES"

# Pin a version for reproducibility; "latest" tracks upstream and can change the corpus.
PLANTUML_VERSION="${PLANTUML_VERSION:-latest}"
if [ "$PLANTUML_VERSION" = "latest" ]; then
  JAR_URL="https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
else
  JAR_URL="https://github.com/plantuml/plantuml/releases/download/v${PLANTUML_VERSION}/plantuml-${PLANTUML_VERSION}.jar"
fi
GUIDE_URL="https://pdf.plantuml.net/PlantUML_Language_Reference_Guide_en.pdf"
GUIDE="$RES/PlantUML_Language_Reference_Guide_en.pdf"

echo "==> plantuml.jar  ($PLANTUML_VERSION)"
curl -fSL --retry 3 -o "$RES/plantuml.jar" "$JAR_URL"
# The backend Dockerfile copies the jar from the build-context root.
cp -f "$RES/plantuml.jar" "$ROOT/backend/plantuml.jar"

echo "==> PlantUML Language Reference Guide"
if [ -f "$GUIDE" ]; then
  echo "    already present, keeping it (this is the RAG corpus - do not replace casually)"
elif curl -fSL --retry 2 -o "$GUIDE" "$GUIDE_URL"; then
  echo "    downloaded"
else
  rm -f "$GUIDE"
  cat >&2 <<'MSG'
    Could not download the guide automatically.
    Get it from https://plantuml.com/guide and save it as
    backend/resources/PlantUML_Language_Reference_Guide_en.pdf
MSG
fi

echo "==> checksums"
if [ -f "$RES/CHECKSUMS.txt" ]; then
  (cd "$RES" && sha256sum -c CHECKSUMS.txt)
else
  (cd "$RES" && sha256sum plantuml.jar ./*.pdf 2>/dev/null > CHECKSUMS.txt) || true
  echo "    wrote $RES/CHECKSUMS.txt - commit it so others resolve the same versions"
fi

echo
echo "Done. Java is required to run plantuml.jar:  java -jar backend/resources/plantuml.jar -version"
