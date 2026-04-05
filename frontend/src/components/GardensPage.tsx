import { useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useEffect, useState, useMemo } from 'react';  // ← добавлен useMemo
import { useQuery } from '@tanstack/react-query';
import { gardenService } from '../services/gardenService';
import { Garden } from '../services/apiConfig';
import { Header } from './Header';
import { SEO } from './SEO';  // ← импорт SEO компонента
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent } from './ui/card';

interface Filters {
  name: string;
  fruit_type: string;
  area_min: string;
  area_max: string;
  search: string;
  sort_by: 'name' | 'area' | 'created_at';
  sort_order: 'asc' | 'desc';
  page: number;
  limit: number;
}

export function GardensPage() {
  const [location] = useSearchParams();  // ← для получения текущего URL
  
  // Вычисляем канонический URL без параметров пагинации/сортировки
  const canonical = useMemo(() => {
    const params = new URLSearchParams(location.toString());
    params.delete('page');
    params.delete('sort_by');
    params.delete('sort_order');
    const queryString = params.toString();
    return queryString ? `/gardens?${queryString}` : '/gardens';
  }, [location]);

  const [searchParams, setSearchParams] = useSearchParams();

  // Инициализация фильтров из URL
  const [filters, setFilters] = useState<Filters>({
    name: searchParams.get('name') || '',
    fruit_type: searchParams.get('fruit_type') || '',
    area_min: searchParams.get('area_min') || '',
    area_max: searchParams.get('area_max') || '',
    search: searchParams.get('search') || '',
    sort_by: (searchParams.get('sort_by') as any) || 'name',
    sort_order: (searchParams.get('sort_order') as any) || 'asc',
    page: Number(searchParams.get('page')) || 1,
    limit: Number(searchParams.get('limit')) || 10,
  });

  // Обновление URL при изменении фильтров
  useEffect(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, val]) => {
      if (val && val !== '') params.set(key, String(val));
    });
    setSearchParams(params);
  }, [filters, setSearchParams]);

  // Запрос данных с бэкенда
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['gardens', filters],
    queryFn: async () => {
      const params = {
        name: filters.name || undefined,
        fruit_type: filters.fruit_type || undefined,
        area_min: filters.area_min ? Number(filters.area_min) : undefined,
        area_max: filters.area_max ? Number(filters.area_max) : undefined,
        search: filters.search || undefined,
        sort_by: filters.sort_by,
        sort_order: filters.sort_order,
        skip: (filters.page - 1) * filters.limit,
        limit: filters.limit,
      };
      const gardens = await gardenService.getAllGardens(params.skip, params.limit);
      
      // Фильтрация на клиенте (временное решение)
      let filtered = gardens;
      if (params.name) filtered = filtered.filter(g => g.name.toLowerCase().includes(params.name!.toLowerCase()));
      if (params.fruit_type) filtered = filtered.filter(g => g.fruit_type === params.fruit_type);
      if (params.area_min) filtered = filtered.filter(g => g.area >= params.area_min!);
      if (params.area_max) filtered = filtered.filter(g => g.area <= params.area_max!);
      if (params.search) {
        filtered = filtered.filter(g => 
          g.name.toLowerCase().includes(params.search!.toLowerCase()) ||
          g.location.toLowerCase().includes(params.search!.toLowerCase())
        );
      }
      // Сортировка
      filtered.sort((a, b) => {
        let aVal: any = a[params.sort_by as keyof Garden];
        let bVal: any = b[params.sort_by as keyof Garden];
        if (params.sort_order === 'asc') return aVal > bVal ? 1 : -1;
        else return aVal < bVal ? 1 : -1;
      });
      return { gardens: filtered, total: filtered.length };
    },
  });

  const handleFilterChange = (key: keyof Filters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  const totalPages = data ? Math.ceil(data.total / filters.limit) : 1;

  return (
    <>
      {/* SEO компонент */}
      <SEO 
        title="Управление садами"
        description="Просмотр, фильтрация и управление садами. Отслеживайте урожайность, площадь и типы плодов в ваших садах."
        canonical={canonical}
        noindex={false}
      />
      
      <div className="min-h-screen bg-background">
        <Header isLoggedIn userName="Администратор" />
        <main className="container mx-auto px-6 py-8 max-w-7xl">
          <h1 className="text-3xl mb-6">Управление садами</h1>

          {/* Блок фильтров */}
          <Card className="mb-8">
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <Label>Название</Label>
                  <Input
                    value={filters.name}
                    onChange={(e) => handleFilterChange('name', e.target.value)}
                    placeholder="Название сада"
                  />
                </div>
                <div>
                  <Label>Тип плодов</Label>
                  <select
                    className="w-full p-2 border rounded"
                    value={filters.fruit_type}
                    onChange={(e) => handleFilterChange('fruit_type', e.target.value)}
                  >
                    <option value="">Все</option>
                    <option value="apple">Яблоки</option>
                    <option value="pear">Груши</option>
                    <option value="cherry">Вишни</option>
                  </select>
                </div>
                <div>
                  <Label>Площадь (га)</Label>
                  <div className="flex gap-2">
                    <Input
                      type="number"
                      value={filters.area_min}
                      onChange={(e) => handleFilterChange('area_min', e.target.value)}
                      placeholder="от"
                    />
                    <Input
                      type="number"
                      value={filters.area_max}
                      onChange={(e) => handleFilterChange('area_max', e.target.value)}
                      placeholder="до"
                    />
                  </div>
                </div>
                <div>
                  <Label>Поиск</Label>
                  <Input
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    placeholder="Название или локация"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <Label>Сортировка по</Label>
                  <select
                    className="w-full p-2 border rounded"
                    value={filters.sort_by}
                    onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                  >
                    <option value="name">Названию</option>
                    <option value="area">Площади</option>
                    <option value="created_at">Дате создания</option>
                  </select>
                </div>
                <div>
                  <Label>Порядок</Label>
                  <select
                    className="w-full p-2 border rounded"
                    value={filters.sort_order}
                    onChange={(e) => handleFilterChange('sort_order', e.target.value)}
                  >
                    <option value="asc">По возрастанию</option>
                    <option value="desc">По убыванию</option>
                  </select>
                </div>
                <div>
                  <Label>На странице</Label>
                  <select
                    className="w-full p-2 border rounded"
                    value={filters.limit}
                    onChange={(e) => handleFilterChange('limit', Number(e.target.value))}
                  >
                    <option value={5}>5</option>
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={50}>50</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" onClick={() => {
                  setFilters({
                    name: '', fruit_type: '', area_min: '', area_max: '', search: '',
                    sort_by: 'name', sort_order: 'asc', page: 1, limit: 10
                  });
                }}>
                  Сбросить фильтры
                </Button>
                <Button onClick={() => refetch()}>Применить</Button>
              </div>
            </CardContent>
          </Card>

          {/* Список садов */}
          {isLoading && <p className="text-center py-8">Загрузка...</p>}
          {!isLoading && data && (
            <>
              <div className="mb-4 text-gray-600">Найдено садов: {data.total}</div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {data.gardens.map(garden => (
                  <div key={garden.id} className="bg-white p-4 rounded shadow">
                    <div className="flex justify-between">
                      <h2 className="font-semibold text-lg">{garden.name}</h2>
                      <span className="text-sm text-gray-500">{garden.fruit_type}</span>
                    </div>
                    <p className="text-gray-600">{garden.location}</p>
                    <p className="text-sm mt-2">Площадь: {garden.area} га</p>
                    {garden.created_at && (
                      <p className="text-xs text-gray-400">Создан: {new Date(garden.created_at).toLocaleDateString()}</p>
                    )}
                  </div>
                ))}
              </div>

              {/* Пагинация */}
              {totalPages > 1 && (
                <div className="flex justify-center gap-2">
                  <Button
                    variant="outline"
                    disabled={filters.page === 1}
                    onClick={() => handleFilterChange('page', filters.page - 1)}
                  >
                    Назад
                  </Button>
                  <span className="py-2 px-4">Страница {filters.page} из {totalPages}</span>
                  <Button
                    variant="outline"
                    disabled={filters.page >= totalPages}
                    onClick={() => handleFilterChange('page', filters.page + 1)}
                  >
                    Вперёд
                  </Button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </>
  );
}