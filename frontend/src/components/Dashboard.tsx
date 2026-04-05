// src/components/Dashboard.tsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Camera, FileText, TrendingUp, Loader2, AlertCircle } from 'lucide-react';
import { Header } from './Header';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { gardenService } from '../services/gardenService';
import { analyticsService } from '../services/analyticsService';
import { analysisService } from '../services/analysisService';
import { useApiRequest } from '../hooks/useApiRequest';
import { GardenWeather } from './GardenWeather';
interface Garden {
  id: number;
  name: string;
  fruit_type: string;
  area: number;
  tree_count?: number;
  harvest_percentage?: number;
}

interface RecentAnalysis {
  id: number;
  time: string;
  tree: string;
  count: number;
  fruit: string;
  accuracy?: number;
}

export function Dashboard() {
  const [gardens, setGardens] = useState<Garden[]>([
    { id: 1, name: 'Яблоневый', fruit_type: 'apple', area: 5, tree_count: 150, harvest_percentage: 85 },
    { id: 2, name: 'Грушевый', fruit_type: 'pear', area: 3, tree_count: 80, harvest_percentage: 60 },
    { id: 3, name: 'Вишневый', fruit_type: 'cherry', area: 2, tree_count: 45, harvest_percentage: 95 },
  ]);
  const [chartData, setChartData] = useState([
    { week: 'Нед 1', count: 120 },
    { week: 'Нед 2', count: 145 },
    { week: 'Нед 3', count: 168 },
    { week: 'Нед 4', count: 195 },
    { week: 'Нед 5', count: 210 },
    { week: 'Нед 6', count: 235 },
  ]);
  const [recentAnalyses, setRecentAnalyses] = useState<RecentAnalysis[]>([
    { id: 1, time: 'Сегодня, 14:30', tree: 'Дерево #45', count: 52, fruit: 'яблок', accuracy: 96 },
    { id: 2, time: 'Сегодня, 11:15', tree: 'Дерево #12', count: 38, fruit: 'яблок', accuracy: 94 },
    { id: 3, time: 'Вчера, 16:20', tree: 'Дерево #78', count: 41, fruit: 'яблок', accuracy: 95 },
    { id: 4, time: '25.09, 09:45', tree: 'Ряд 1-10', count: 425, fruit: 'яблок', accuracy: 94 },
  ]);
  
  const gardensRequest = useApiRequest<Garden[]>();
  const analyticsRequest = useApiRequest<any>();
  const historyRequest = useApiRequest<any>();
  
  // Получаем имя пользователя из localStorage
  const getUserName = () => {
    try {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        return user.full_name || user.email ;
      }
    } catch (error) {
      console.error('Ошибка при получении пользователя:', error);
    }
    return ' ';
  };
  
  // Функция для получения иконки по типу фрукта
  const getFruitIcon = (fruitType: string) => {
    switch (fruitType?.toLowerCase()) {
      case 'apple': return '🍎';
      case 'pear': return '🍐';
      case 'cherry': return '🍒';
      case 'plum': return '🟣';
      default: return '🌳';
    }
  };
  
  // Форматирование процента урожая
  const formatHarvestPercentage = (percentage?: number) => {
    if (percentage === undefined) return '0%';
    return `${Math.min(Math.round(percentage), 100)}%`;
  };
  
  // Загрузка данных при монтировании компонента
  useEffect(() => {
    loadDashboardData();
  }, []);
  
  const loadDashboardData = async () => {
    try {
      // Загружаем сады с бэкенда
      const gardensData = await gardensRequest.execute(() => 
        gardenService.getAllGardens()
      );
      
      if (gardensData.length > 0) {
        // Обновляем сады с данными из бэкенда
        const updatedGardens = await Promise.all(
          gardensData.slice(0, 3).map(async (garden) => {
            try {
              // Получаем статистику для каждого сада
              const stats = await gardenService.getGardenStats(garden.id);
              return {
                ...garden,
                tree_count: stats.total_trees || 0,
                harvest_percentage: stats.average_fruits_per_tree || 0,
              };
            } catch (error) {
              console.error(`Ошибка при загрузке статистики для сада ${garden.id}:`, error);
              return garden;
            }
          })
        );
        setGardens(updatedGardens);
        
        // Загружаем аналитику для первого сада
        if (gardensData.length > 0) {
          const analytics = await analyticsRequest.execute(() =>
            analyticsService.getGrowth(gardensData[0].id)
          );
          
          if (analytics.weekly_data) {
            // Преобразуем данные для графика
            const newChartData = analytics.weekly_data.map((item: any) => ({
              week: item.week,
              count: item.fruits
            }));
            setChartData(newChartData);
          }
        }
        
        // Загружаем историю анализов
        const history = await historyRequest.execute(() =>
          analysisService.getAnalysisHistory(gardensData[0]?.id, undefined, 4)
        );
        
        if (history.analyses && history.analyses.length > 0) {
          // Преобразуем данные истории
          const formattedHistory: RecentAnalysis[] = history.analyses.map((item: any, index: number) => ({
            id: item.id,
            time: formatDate(item.harvest_date),
            tree: item.tree_id ? `Дерево #${item.tree_id}` : 'Автоопределение',
            count: item.fruit_count,
            fruit: getFruitName(gardensData[0]?.fruit_type || 'apple'),
            accuracy: Math.round((item.confidence || 0.95) * 100)
          }));
          setRecentAnalyses(formattedHistory);
        }
      }
    } catch (error) {
      console.error('Ошибка загрузки данных дашборда:', error);
      // Оставляем статические данные в случае ошибки
    }
  };
  
  // Функция для форматирования даты
  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'Недавно';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) {
      return 'Только что';
    } else if (diffHours < 24) {
      return `Сегодня, ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    } else if (diffHours < 48) {
      return `Вчера, ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    } else {
      return `${date.getDate().toString().padStart(2, '0')}.${(date.getMonth() + 1).toString().padStart(2, '0')}, ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    }
  };
  
  // Функция для получения названия фрукта
  const getFruitName = (fruitType: string): string => {
    switch (fruitType.toLowerCase()) {
      case 'apple': return 'яблок';
      case 'pear': return 'груш';
      case 'cherry': return 'вишен';
      case 'plum': return 'слив';
      default: return 'плодов';
    }
  };
  
  // Рассчитываем процент роста урожая
  const calculateGrowthPercentage = () => {
    if (chartData.length < 2) return 18;
    const first = chartData[0].count;
    const last = chartData[chartData.length - 1].count;
    return Math.round(((last - first) / first) * 100);
  };
  
  const isLoading = gardensRequest.loading || analyticsRequest.loading || historyRequest.loading;
  const hasError = gardensRequest.error || analyticsRequest.error || historyRequest.error;
  const userName = getUserName();
  
  return (
    <div className="min-h-screen bg-background">
      <Header isLoggedIn userName={userName} />
      
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl mb-2">Добро пожаловать, {userName}! 🍎</h1>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={loadDashboardData}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <TrendingUp className="size-4" />
              )}
              Обновить
            </Button>
          </div>
          
          {hasError && (
            <div className="flex items-center gap-2 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg mt-2">
              <AlertCircle className="size-5" />
              <span>Не удалось загрузить некоторые данные. Показаны статические данные.</span>
            </div>
          )}
          
          {isLoading && (
            <div className="flex items-center gap-2 p-3 bg-blue-100 border border-blue-400 text-blue-700 rounded-lg mt-2">
              <Loader2 className="size-5 animate-spin" />
              <span>Загрузка данных...</span>
            </div>
          )}
        </div>
        
        {/* Gardens Overview */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">📊</span>
            <h2 className="text-2xl">ОБЗОР ВАШИХ САДОВ:</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {gardens.map((garden, index) => (
              <Card 
                key={garden.id || index}
                className="border-2 hover:border-primary transition-all duration-300 cursor-pointer hover:shadow-lg hover:scale-[1.02]"
                onClick={() => {/* Навигация к деталям сада */}}
              >
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="text-4xl">{getFruitIcon(garden.fruit_type)}</div>
                    {isLoading && (
                      <Loader2 className="size-5 animate-spin text-muted-foreground" />
                    )}
                  </div>
                  
                  <h3 className="mb-2 text-xl font-semibold">
                    {garden.name}
                  </h3>
                  
                  <p className="text-muted-foreground mb-1">
                    {garden.tree_count || '?'} деревьев
                  </p>
                    <div className="mt-2">
                      <GardenWeather 
                        gardenId={garden.id} 
                        lat={55.751244} 
                        lon={37.618423} 
                      />
                    </div>
                  <div className="mt-4">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-muted-foreground">Урожайность:</span>
                      <span className="text-primary font-semibold">
                        {formatHarvestPercentage(garden.harvest_percentage)}
                      </span>
                    </div>
                    
                    <div className="w-full bg-secondary rounded-full h-2.5">
                      <div 
                        className="bg-primary h-2.5 rounded-full transition-all duration-500"
                        style={{ 
                          width: `${Math.min(garden.harvest_percentage || 0, 100)}%`,
                          opacity: isLoading ? 0.5 : 1 
                        }}
                      ></div>
                    </div>
                    
                    <p className="text-xs text-muted-foreground mt-2">
                      Площадь: {garden.area} га
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {/* Карточка для создания нового сада */}
            {gardens.length < 3 && !isLoading && (
              <Card className="border-2 border-dashed border-muted-foreground/30 hover:border-primary transition-colors cursor-pointer">
                <CardContent className="pt-6 flex flex-col items-center justify-center h-full min-h-[200px]">
                  <div className="text-4xl mb-4">+</div>
                  <h3 className="mb-2 text-center">Добавить новый сад</h3>
                  <p className="text-muted-foreground text-center text-sm">
                    Начните отслеживать новый сад
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
        
        {/* Quick Actions */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">🎯</span>
            <h2 className="text-2xl">БЫСТРЫЕ ДЕЙСТВИЯ:</h2>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <Button 
              size="lg" 
              asChild
              className="flex-1"
              disabled={isLoading}
            >
              <Link to="/analysis" className="flex items-center justify-center gap-2">
                <Camera className="size-5" />
                ЗАГРУЗИТЬ ФОТО ДЛЯ АНАЛИЗА
              </Link>
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              asChild
              className="flex-1"
              disabled={isLoading}
            >
              <Link to="/analytics" className="flex items-center justify-center gap-2">
                <FileText className="size-5" />
                ПОСМОТРЕТЬ ОТЧЕТЫ
              </Link>
            </Button>
          </div>
        </div>
        
        {/* Harvest Dynamics Chart */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">📈</span>
            <h2 className="text-2xl">ДИНАМИКА УРОЖАЙНОСТИ ({gardens[0]?.name || 'Яблоневый'} сад):</h2>
          </div>
          
          <Card>
            <CardContent className="pt-6">
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart 
                    data={chartData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid 
                      strokeDasharray="3 3" 
                      stroke="#E0E0E0" 
                      vertical={false}
                    />
                    <XAxis 
                      dataKey="week" 
                      stroke="#757575"
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis 
                      stroke="#757575"
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(value) => `${value}`}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        borderRadius: '8px',
                        border: '1px solid #e0e0e0',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                      }}
                      formatter={(value: number) => [`${value} плодов`, 'Количество']}
                      labelFormatter={(label) => `Неделя: ${label}`}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="count" 
                      stroke="#4CAF50" 
                      strokeWidth={3}
                      dot={{ 
                        fill: '#4CAF50', 
                        r: 5,
                        strokeWidth: 2,
                        stroke: '#fff'
                      }}
                      activeDot={{ 
                        r: 7, 
                        fill: '#2E7D32',
                        stroke: '#fff',
                        strokeWidth: 2
                      }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              
              <div className="mt-6 p-4 bg-secondary/10 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-muted-foreground">Среднее количество плодов:</p>
                    <p className="text-2xl font-semibold">
                      {Math.round(chartData.reduce((sum, item) => sum + item.count, 0) / chartData.length)}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Рост урожая:</p>
                    <p className="text-2xl font-semibold text-green-600">
                      +{calculateGrowthPercentage()}%
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Всего плодов:</p>
                    <p className="text-2xl font-semibold">
                      {chartData.reduce((sum, item) => sum + item.count, 0)}
                    </p>
                  </div>
                </div>
                
                <p className="text-center text-muted-foreground mt-4">
                  Сентябрь 2024 → Урожай растет на {calculateGrowthPercentage()}% в неделю
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Recent Analyses */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🗓</span>
              <h2 className="text-2xl">ПОСЛЕДНИЕ АНАЛИЗЫ:</h2>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              asChild
              disabled={isLoading}
            >
              <Link to="/history" className="text-primary hover:text-primary/80">
                Вся история →
              </Link>
            </Button>
          </div>
          
          <Card>
            <CardContent className="pt-6">
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="size-8 animate-spin text-muted-foreground" />
                </div>
              ) : recentAnalyses.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-muted-foreground mb-4">Нет данных об анализах</p>
                  <Button asChild>
                    <Link to="/analysis">Создать первый анализ</Link>
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {recentAnalyses.map((analysis) => (
                    <div 
                      key={analysis.id} 
                      className="flex items-center justify-between py-4 border-b last:border-0 hover:bg-secondary/10 px-2 rounded-lg transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className="bg-primary/10 p-2 rounded-lg">
                          <span className="text-xl">{getFruitIcon(analysis.fruit)}</span>
                        </div>
                        
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-muted-foreground text-sm">{analysis.time}</span>
                            <span className="text-muted-foreground">•</span>
                            <span className="font-medium">{analysis.tree}</span>
                            <span className="text-muted-foreground">→</span>
                            <span className="text-primary font-semibold">
                              {analysis.count} {analysis.fruit}
                            </span>
                          </div>
                          
                          {analysis.accuracy && (
                            <div className="flex items-center gap-2 mt-1">
                              <div className="w-16 bg-secondary rounded-full h-1.5">
                                <div 
                                  className="bg-green-500 h-1.5 rounded-full"
                                  style={{ width: `${analysis.accuracy}%` }}
                                ></div>
                              </div>
                              <span className="text-xs text-muted-foreground">
                                {analysis.accuracy}% точность
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        {analysis.accuracy && analysis.accuracy >= 95 ? (
                          <span className="text-green-600 font-medium">✅ Отлично</span>
                        ) : analysis.accuracy && analysis.accuracy >= 90 ? (
                          <span className="text-blue-600 font-medium">👍 Хорошо</span>
                        ) : (
                          <span className="text-amber-600 font-medium">⚠️ Проверить</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Статистика внизу */}
              {recentAnalyses.length > 0 && !isLoading && (
                <div className="mt-6 pt-4 border-t">
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                        <span>Высокая точность (&gt;95%)</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                        <span>Хорошая точность (90-95%)</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-amber-500 rounded-full"></div>
                        <span>Требует проверки (&lt;90%)</span>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p>Средняя точность: <span className="font-semibold text-foreground">
                        {Math.round(recentAnalyses.reduce((sum, a) => sum + (a.accuracy || 0), 0) / recentAnalyses.length)}%
                      </span></p>
                      <p>Всего анализов: <span className="font-semibold text-foreground">{recentAnalyses.length}</span></p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}