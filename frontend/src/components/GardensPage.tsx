import { useSearchParams } from 'react-router-dom';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useQuery } from '@tanstack/react-query';
import { gardenService } from '../services/gardenService';
import { Garden } from '../services/apiConfig';
import { useEffect } from 'react';
import { useForm, Resolver } from 'react-hook-form';

// Определяем схему с правильными типами
const filterSchema = z.object({
  name: z.string(),
  fruit_type: z.string(),
  area_min: z.number().min(0).optional(),
  area_max: z.number().min(0).optional(),
  sort_by: z.enum(['name', 'area', 'created_at']),
  sort_order: z.enum(['asc', 'desc']),
  page: z.number().min(1),
  limit: z.number().min(1).max(100),
});

// Явно указываем тип для формы
type FilterValues = {
  name: string;
  fruit_type: string;
  area_min?: number;
  area_max?: number;
  sort_by: 'name' | 'area' | 'created_at';
  sort_order: 'asc' | 'desc';
  page: number;
  limit: number;
};

// Создаём resolver с правильным приведением типа
const resolver = zodResolver(filterSchema) as unknown as Resolver<FilterValues>;

interface GardenQueryParams {
  name?: string;
  fruit_type?: string;
  area_min?: number;
  area_max?: number;
  sort_by?: string;
  sort_order?: string;
  skip?: number;
  limit?: number;
}

export function GardensPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Функция для получения значений по умолчанию из URL
  const getDefaultValues = (): FilterValues => {
    return {
      name: searchParams.get('name') || '',
      fruit_type: searchParams.get('fruit_type') || '',
      area_min: searchParams.get('area_min') ? Number(searchParams.get('area_min')) : undefined,
      area_max: searchParams.get('area_max') ? Number(searchParams.get('area_max')) : undefined,
      sort_by: (searchParams.get('sort_by') as FilterValues['sort_by']) || 'name',
      sort_order: (searchParams.get('sort_order') as FilterValues['sort_order']) || 'asc',
      page: Number(searchParams.get('page')) || 1,
      limit: Number(searchParams.get('limit')) || 10,
    };
  };

  // Используем form с явным типом
  const form = useForm<FilterValues>({
    resolver,
    defaultValues: getDefaultValues(),
  });

  const filters = form.watch();

  // Синхронизация с URL
  useEffect(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, val]) => {
      if (val !== undefined && val !== '') {
        params.set(key, String(val));
      }
    });
    setSearchParams(params);
  }, [filters, setSearchParams]);

  // Остальной код без изменений...
  const getQueryParams = (filters: FilterValues): GardenQueryParams => {
    const params: GardenQueryParams = {
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
      skip: (filters.page - 1) * filters.limit,
      limit: filters.limit,
    };
    
    if (filters.name) params.name = filters.name;
    if (filters.fruit_type) params.fruit_type = filters.fruit_type;
    if (filters.area_min !== undefined) params.area_min = filters.area_min;
    if (filters.area_max !== undefined) params.area_max = filters.area_max;
    
    return params;
  };

  // Запрос данных
  const { data, isLoading } = useQuery<{ gardens: Garden[]; total: number }>({
    queryKey: ['gardens', filters],
    queryFn: async () => {
      const params = getQueryParams(filters);
      const gardens = await gardenService.getAllGardens(
        params.skip || 0,
        params.limit || 10
      );
      
      // Фильтрация на клиенте
      let filteredGardens = [...gardens];
      
      if (params.name) {
        filteredGardens = filteredGardens.filter(g => 
          g.name.toLowerCase().includes(params.name!.toLowerCase())
        );
      }
      
      if (params.fruit_type) {
        filteredGardens = filteredGardens.filter(g => 
          g.fruit_type === params.fruit_type
        );
      }
      
      if (params.area_min !== undefined) {
        filteredGardens = filteredGardens.filter(g => g.area >= params.area_min!);
      }
      
      if (params.area_max !== undefined) {
        filteredGardens = filteredGardens.filter(g => g.area <= params.area_max!);
      }
      
      // Сортировка
      filteredGardens.sort((a, b) => {
        let aVal: string | number = a[params.sort_by as keyof Garden] as string | number;
        let bVal: string | number = b[params.sort_by as keyof Garden] as string | number;
        
        if (params.sort_order === 'asc') {
          return aVal > bVal ? 1 : -1;
        } else {
          return aVal < bVal ? 1 : -1;
        }
      });
      
      return {
        gardens: filteredGardens,
        total: filteredGardens.length
      };
    },
  });

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Управление садами</h1>
      
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <h2 className="text-lg font-semibold mb-4">Фильтры</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Название</label>
            <input 
              {...form.register('name')} 
              placeholder="Название сада"
              className="w-full p-2 border rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Тип плодов</label>
            <select {...form.register('fruit_type')} className="w-full p-2 border rounded">
              <option value="">Все типы</option>
              <option value="apple">🍎 Яблоки</option>
              <option value="pear">🍐 Груши</option>
              <option value="cherry">🍒 Вишни</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Площадь (га)</label>
            <div className="flex gap-2">
              <input 
                type="number" 
                {...form.register('area_min', { valueAsNumber: true })} 
                placeholder="От"
                className="w-1/2 p-2 border rounded"
              />
              <input 
                type="number" 
                {...form.register('area_max', { valueAsNumber: true })} 
                placeholder="До"
                className="w-1/2 p-2 border rounded"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Сортировка</label>
            <select {...form.register('sort_by')} className="w-full p-2 border rounded">
              <option value="name">По названию</option>
              <option value="area">По площади</option>
              <option value="created_at">По дате создания</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Порядок</label>
            <select {...form.register('sort_order')} className="w-full p-2 border rounded">
              <option value="asc">По возрастанию</option>
              <option value="desc">По убыванию</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">На странице</label>
            <select {...form.register('limit', { valueAsNumber: true })} className="w-full p-2 border rounded">
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
            </select>
          </div>
        </div>
        
        <div className="mt-4 flex gap-2">
          <button 
            type="button"
            onClick={() => form.reset(getDefaultValues())}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Сбросить фильтры
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="text-center py-8">
          <p className="text-gray-500">Загрузка садов...</p>
        </div>
      )}
      
      {!isLoading && data?.gardens && (
        <>
          <div className="mb-4 flex justify-between items-center">
            <p className="text-gray-600">Найдено садов: <span className="font-semibold">{data.total}</span></p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {data.gardens.map((garden: Garden) => (
              <div key={garden.id} className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg">{garden.name}</h3>
                    <p className="text-sm text-gray-500">{garden.location}</p>
                  </div>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                    {garden.fruit_type === 'apple' && '🍎'}
                    {garden.fruit_type === 'pear' && '🍐'}
                    {garden.fruit_type === 'cherry' && '🍒'}
                  </span>
                </div>
                <div className="mt-2 flex justify-between items-center">
                  <span className="text-gray-600">Площадь:</span>
                  <span className="font-medium">{garden.area} га</span>
                </div>
                {garden.created_at && (
                  <div className="mt-1 text-xs text-gray-400">
                    Создан: {new Date(garden.created_at).toLocaleDateString()}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Пагинация */}
          {data.total > filters.limit && (
            <div className="flex items-center justify-center gap-4 mt-6">
              <button 
                onClick={() => form.setValue('page', filters.page - 1)} 
                disabled={filters.page === 1}
                className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300 hover:bg-blue-600 transition-colors"
              >
                ← Назад
              </button>
              <span className="text-lg font-medium">
                Страница {filters.page} из {Math.ceil(data.total / filters.limit)}
              </span>
              <button 
                onClick={() => form.setValue('page', filters.page + 1)}
                disabled={filters.page >= Math.ceil(data.total / filters.limit)}
                className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300 hover:bg-blue-600 transition-colors"
              >
                Вперёд →
              </button>
            </div>
          )}
        </>
      )}
      
      {!isLoading && data?.gardens.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500 text-lg mb-2">Сады не найдены</p>
          <p className="text-gray-400">Попробуйте изменить параметры фильтрации</p>
          <button 
            onClick={() => form.reset(getDefaultValues())}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Сбросить фильтры
          </button>
        </div>
      )}
    </div>
  );
}