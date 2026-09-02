/**
 * SettingsPage Component
 * User account settings with change password and delete account
 */

import { useState } from 'react';
import { ArrowLeft, Key, Trash2 } from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Label,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '../components/ui';

interface SettingsPageProps {
  onBack: () => void;
}

export function SettingsPage({ onBack }: SettingsPageProps) {
  const { isLoading, error, changePassword, deleteAccount, clearError } = useAuthStore();

  // Change password state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  // Delete account state
  const [deletePassword, setDeletePassword] = useState('');
  const [confirmDelete, setConfirmDelete] = useState('');

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setPasswordSuccess(false);

    if (newPassword !== confirmPassword) {
      return;
    }

    const success = await changePassword(currentPassword, newPassword);
    if (success) {
      setPasswordSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    }
  };

  const handleDeleteAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    if (confirmDelete !== 'DELETE') {
      return;
    }

    await deleteAccount(deletePassword, confirmDelete);
  };

  return (
    <div className="min-h-screen bg-muted p-6">
      <div className="max-w-2xl mx-auto">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>

        <Card>
          <CardHeader>
            <CardTitle>Account Settings</CardTitle>
            <CardDescription>
              Manage your account security and preferences
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="password">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="password">
                  <Key className="h-4 w-4 mr-2" />
                  Password
                </TabsTrigger>
                <TabsTrigger value="delete">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Account
                </TabsTrigger>
              </TabsList>

              <TabsContent value="password" className="mt-6">
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="current-password">Current Password</Label>
                    <Input
                      id="current-password"
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      placeholder="Enter current password"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="new-password">New Password</Label>
                    <Input
                      id="new-password"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Enter new password (min 6 characters)"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirm-password">Confirm New Password</Label>
                    <Input
                      id="confirm-password"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Confirm new password"
                    />
                    {newPassword && confirmPassword && newPassword !== confirmPassword && (
                      <p className="text-sm text-destructive">Passwords do not match</p>
                    )}
                  </div>

                  {error && (
                    <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                      {error}
                    </div>
                  )}

                  {passwordSuccess && (
                    <div className="p-3 rounded-md bg-emerald-500/10 text-emerald-600 text-sm">
                      Password changed successfully
                    </div>
                  )}

                  <Button
                    type="submit"
                    isLoading={isLoading}
                    disabled={!currentPassword || !newPassword || !confirmPassword || newPassword !== confirmPassword}
                  >
                    Change Password
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="delete" className="mt-6">
                <div className="p-4 rounded-md bg-destructive/10 border border-destructive/20 mb-6">
                  <h3 className="font-medium text-destructive mb-2">Warning</h3>
                  <p className="text-sm text-destructive/80">
                    This action is permanent and cannot be undone. All your data will be deleted.
                  </p>
                </div>

                <form onSubmit={handleDeleteAccount} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="delete-password">Password</Label>
                    <Input
                      id="delete-password"
                      type="password"
                      value={deletePassword}
                      onChange={(e) => setDeletePassword(e.target.value)}
                      placeholder="Enter your password"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirm-delete">
                      Type <span className="font-mono font-bold">DELETE</span> to confirm
                    </Label>
                    <Input
                      id="confirm-delete"
                      type="text"
                      value={confirmDelete}
                      onChange={(e) => setConfirmDelete(e.target.value)}
                      placeholder="DELETE"
                    />
                  </div>

                  {error && (
                    <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                      {error}
                    </div>
                  )}

                  <Button
                    type="submit"
                    variant="destructive"
                    isLoading={isLoading}
                    disabled={!deletePassword || confirmDelete !== 'DELETE'}
                  >
                    Delete Account
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
