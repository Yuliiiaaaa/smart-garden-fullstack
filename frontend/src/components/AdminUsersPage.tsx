// src/components/AdminUsersPage.tsx
import { useState, useEffect } from 'react';
import { Header } from './Header';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { userService } from '../services/userService';
import { useApiRequest } from '../hooks/useApiRequest';
import { User } from '../services/apiConfig';
import { toast } from 'sonner';

export function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [editingUserId, setEditingUserId] = useState<number | null>(null);
  const usersRequest = useApiRequest<User[]>();
  const updateRoleRequest = useApiRequest<User>();

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await usersRequest.execute(() => userService.getAllUsers());
      setUsers(data);
    } catch (error) {
      toast.error('Не удалось загрузить список пользователей');
    }
  };

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      const updated = await updateRoleRequest.execute(() =>
        userService.changeUserRole(userId, newRole)
      );
      setUsers(users.map(u => u.id === userId ? updated : u));
      setEditingUserId(null);
      toast.success('Роль пользователя обновлена');
    } catch (error) {
      toast.error('Ошибка при обновлении роли');
    }
  };

  // Функция для отображения роли на русском
  const getRoleDisplay = (role: string): string => {
    switch (role) {
      case 'admin': return 'Администратор';
      case 'manager': return 'Менеджер';
      case 'user': return 'Пользователь';
      default: return role;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header isLoggedIn userName="Администратор" />
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl mb-2 flex items-center gap-2">
            <span className="text-2xl">👥</span>
            УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
          </h1>
          <p className="text-muted-foreground">
            Изменение ролей пользователей (доступно только администратору)
          </p>
        </div>

        <Card>
          <CardContent className="pt-6">
            {usersRequest.loading && (
              <div className="text-center py-8">
                <p className="text-muted-foreground">Загрузка пользователей...</p>
              </div>
            )}
            
            {usersRequest.error && (
              <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                {usersRequest.error}
              </div>
            )}

            {!usersRequest.loading && !usersRequest.error && (
              <div className="space-y-4">
                {users.length === 0 ? (
                  <p className="text-center py-8 text-muted-foreground">
                    Пользователи не найдены
                  </p>
                ) : (
                  users.map(user => (
                    <div 
                      key={user.id} 
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-secondary/10 transition-colors"
                    >
                      <div className="flex-1">
                        <p className="font-semibold">{user.full_name}</p>
                        <p className="text-sm text-muted-foreground">{user.email}</p>
                      </div>

                      {editingUserId === user.id ? (
                        <div className="flex items-center gap-2">
                          <Select
                            defaultValue={user.role}
                            onValueChange={(value: string) => handleRoleChange(user.id, value)}
                          >
                            <SelectTrigger className="w-40">
                              <SelectValue placeholder="Выберите роль" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="user">👤 Пользователь</SelectItem>
                              <SelectItem value="manager">📊 Менеджер</SelectItem>
                              <SelectItem value="admin">⚡ Администратор</SelectItem>
                            </SelectContent>
                          </Select>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => setEditingUserId(null)}
                          >
                            Отмена
                          </Button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-4">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            user.role === 'admin' ? 'bg-purple-100 text-purple-700' :
                            user.role === 'manager' ? 'bg-blue-100 text-blue-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {getRoleDisplay(user.role)}
                          </span>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => setEditingUserId(user.id)}
                          >
                            Изменить роль
                          </Button>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Информация о ролях */}
        <div className="mt-8 grid grid-cols-3 gap-4">
          <Card className="bg-purple-50 border-purple-200">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">⚡</span>
                <h3 className="font-semibold">Администратор</h3>
              </div>
              <p className="text-sm text-purple-700">
                Полный доступ ко всем функциям, управление пользователями, удаление садов
              </p>
            </CardContent>
          </Card>

          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">📊</span>
                <h3 className="font-semibold">Менеджер</h3>
              </div>
              <p className="text-sm text-blue-700">
                Создание и редактирование садов, просмотр всей аналитики
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-50 border-gray-200">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">👤</span>
                <h3 className="font-semibold">Пользователь</h3>
              </div>
              <p className="text-sm text-gray-700">
                Базовый доступ: анализ фото, история, своя статистика
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}