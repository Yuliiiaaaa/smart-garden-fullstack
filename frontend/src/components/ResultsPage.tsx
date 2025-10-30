import { Link } from 'react-router-dom';
import { Save, FileText, RefreshCw } from 'lucide-react';
import { Header } from './Header';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { ImageWithFallback } from './figma/ImageWithFallback';

export function ResultsPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header isLoggedIn userName="Иван" />
      
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">✅</span>
            <h1 className="text-3xl">АНАЛИЗ ЗАВЕРШЕН</h1>
          </div>
          <p className="text-muted-foreground">
            Время обработки: 3.2 секунды | Точность: 94%
          </p>
        </div>
        
        <div className="grid grid-cols-2 gap-8 mb-8">
          {/* Image with Markup */}
          <Card>
            <CardContent className="pt-6">
              <div className="relative aspect-video bg-muted rounded-lg overflow-hidden mb-4">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1694132149888-8bd893e3029b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhcHBsZSUyMHRyZWUlMjBmcnVpdHN8ZW58MXx8fHwxNzU5MzI4NjczfDA&ixlib=rb-4.1.0&q=80&w=1080"
                  alt="Анализируемое дерево"
                  className="size-full object-cover"
                />
                {/* Simulated detection boxes overlay */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center bg-black/50 text-white p-4 rounded-lg">
                    <p className="text-sm">Зеленые рамки - обнаруженные плоды</p>
                    <p className="text-sm">Красные рамки - возможные ошибки</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Analysis Results */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-6">
                <span className="text-2xl">📊</span>
                <h2 className="text-2xl">РЕЗУЛЬТАТЫ АНАЛИЗА:</h2>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center gap-3 p-4 bg-secondary/20 rounded-lg">
                  <span className="text-3xl">🍎</span>
                  <div>
                    <p className="text-muted-foreground">Обнаружено плодов:</p>
                    <p className="text-3xl text-primary">42</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                  <span className="text-2xl">📏</span>
                  <div>
                    <p className="text-muted-foreground">Средний размер:</p>
                    <p className="text-xl">6.5 см</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                  <span className="text-2xl">🎯</span>
                  <div>
                    <p className="text-muted-foreground">Точность:</p>
                    <p className="text-xl">94%</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                  <span className="text-2xl">🌳</span>
                  <div>
                    <p className="text-muted-foreground">Определено:</p>
                    <p className="text-xl">Яблоня</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                  <span className="text-2xl">📍</span>
                  <div>
                    <p className="text-muted-foreground">Дерево:</p>
                    <p className="text-xl">#15 (авто)</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* AI Comment */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">📝</span>
            <h2 className="text-2xl">КОММЕНТАРИЙ ИИ:</h2>
          </div>
          
          <Card className="bg-secondary/10">
            <CardContent className="pt-6">
              <p className="text-lg">
                "На дереве обнаружено 42 яблока. Плоды равномерно распределены по кроне. 
                Рекомендуется сбор через 7-10 дней."
              </p>
            </CardContent>
          </Card>
        </div>
        
        {/* Action Buttons */}
        <div className="flex gap-4 justify-center mb-8">
          <Button size="lg" className="flex items-center gap-2">
            <Save className="size-5" />
            СОХРАНИТЬ РЕЗУЛЬТАТ
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link to="/analytics" className="flex items-center gap-2">
              <FileText className="size-5" />
              ДОБАВИТЬ В ОТЧЕТ
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link to="/analysis" className="flex items-center gap-2">
              <RefreshCw className="size-5" />
              НОВЫЙ АНАЛИЗ
            </Link>
          </Button>
        </div>
        
        {/* Recommendations */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">🎯</span>
            <h2 className="text-2xl">РЕКОМЕНДАЦИИ:</h2>
          </div>
          
          <Card>
            <CardContent className="pt-6">
              <ul className="space-y-3">
                <li className="flex items-start gap-2">
                  <span>•</span>
                  <span>Оптимальное время сбора: 02-09 октября</span>
                </li>
                <li className="flex items-start gap-2">
                  <span>•</span>
                  <span>Ожидаемый вес урожая: ~12.5 кг</span>
                </li>
                <li className="flex items-start gap-2">
                  <span>•</span>
                  <span>Рекомендуется проверить соседние деревья ряда 2</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}