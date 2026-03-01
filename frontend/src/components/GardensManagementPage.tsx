// src/components/GardensManagementPage.tsx
import { useState, useEffect } from 'react';
import { Header } from './Header';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { gardenService } from '../services/gardenService';
import { useApiRequest } from '../hooks/useApiRequest';
import { Garden } from '../services/apiConfig';
import { toast } from 'sonner';

export function GardensManagementPage() {
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [newGarden, setNewGarden] = useState({
    name: '',
    location: '',          // добавлено поле location
    fruit_type: 'apple',
    area: 1
  });
  const gardensRequest = useApiRequest<Garden[]>();
  const createRequest = useApiRequest<Garden>();
  const deleteRequest = useApiRequest<any>();

  useEffect(() => {
    loadGardens();
  }, []);

  const loadGardens = async () => {
    try {
      const data = await gardensRequest.execute(() => gardenService.getAllGardens());
      setGardens(data);
    } catch (error) {
      toast.error('Не удалось загрузить сады');
    }
  };

  const handleCreate = async () => {
    if (!newGarden.name) {
      toast.error('Введите название сада');
      return;
    }
    if (!newGarden.location) {
      toast.error('Введите местоположение сада');
      return;
    }
    try {
      const created = await createRequest.execute(() =>
        gardenService.createGarden(newGarden)
      );
      setGardens([...gardens, created]);
      setNewGarden({ name: '', location: '', fruit_type: 'apple', area: 1 });
      toast.success('Сад создан');
    } catch (error) {
      toast.error('Ошибка при создании сада');
    }
  };

  const handleDelete = async (gardenId: number) => {
    if (!confirm('Удалить сад? Это действие необратимо.')) return;
    try {
      await deleteRequest.execute(() => gardenService.deleteGarden(gardenId));
      setGardens(gardens.filter(g => g.id !== gardenId));
      toast.success('Сад удалён');
    } catch (error) {
      toast.error('Ошибка при удалении');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header isLoggedIn userName="Менеджер" />
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        <h1 className="text-3xl mb-6">Управление садами</h1>

        {/* Форма создания нового сада */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <h2 className="text-xl mb-4">Добавить новый сад</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Название</Label>
                <Input
                  value={newGarden.name}
                  onChange={(e) => setNewGarden({ ...newGarden, name: e.target.value })}
                  placeholder="Например: Яблоневый сад"
                />
              </div>
              <div>
                <Label>Местоположение</Label>
                <Input
                  value={newGarden.location}
                  onChange={(e) => setNewGarden({ ...newGarden, location: e.target.value })}
                  placeholder="Например: Северный участок, ряд 1-10"
                />
              </div>
              <div>
                <Label>Тип плодов</Label>
                <select
                  className="w-full p-2 border rounded"
                  value={newGarden.fruit_type}
                  onChange={(e) => setNewGarden({ ...newGarden, fruit_type: e.target.value })}
                >
                  <option value="apple">🍎 Яблоки</option>
                  <option value="pear">🍐 Груши</option>
                  <option value="cherry">🍒 Вишни</option>
                </select>
              </div>
              <div>
                <Label>Площадь (га)</Label>
                <Input
                  type="number"
                  min="0.1"
                  step="0.1"
                  value={newGarden.area}
                  onChange={(e) => setNewGarden({ ...newGarden, area: parseFloat(e.target.value) })}
                />
              </div>
            </div>
            <Button onClick={handleCreate} className="mt-4" disabled={createRequest.loading}>
              {createRequest.loading ? 'Создание...' : '➕ Создать сад'}
            </Button>
          </CardContent>
        </Card>

        {/* Список садов с возможностью удаления */}
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-xl mb-4">Существующие сады</h2>
            {gardensRequest.loading && (
              <div className="text-center py-4">Загрузка...</div>
            )}
            {gardensRequest.error && (
              <div className="text-center py-4 text-red-600">{gardensRequest.error}</div>
            )}
            <div className="space-y-2">
              {gardens.map(garden => (
                <div key={garden.id} className="flex items-center justify-between p-3 border rounded hover:bg-secondary/10">
                  <div>
                    <span className="font-semibold">{garden.name}</span>
                    <span className="ml-4 text-sm text-muted-foreground">
                      {garden.location} | {garden.fruit_type}, {garden.area} га
                    </span>
                  </div>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDelete(garden.id)}
                    disabled={deleteRequest.loading}
                  >
                    Удалить
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}