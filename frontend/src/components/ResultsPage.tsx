// src/components/ResultsPage.tsx (обновленный)
import { useLocation, Link } from 'react-router-dom';
import { Save, FileText, RefreshCw } from 'lucide-react';
import { Header } from './Header';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { AnalysisResult } from '../services/apiConfig';

interface LocationState {
  analysisResult?: AnalysisResult;
}

export function ResultsPage() {
  const location = useLocation();
  const state = location.state as LocationState;
  const result = state?.analysisResult;
  
  // Если нет данных, показываем заглушку
  if (!result) {
    return (
      <div className="min-h-screen bg-background">
        <Header isLoggedIn userName="Иван" />
        <main className="container mx-auto px-6 py-8 max-w-7xl">
          <div className="text-center py-16">
            <h1 className="text-2xl mb-4">Данные анализа не найдены</h1>
            <p className="text-muted-foreground mb-6">
              Пожалуйста, выполните анализ изображения
            </p>
            <Button asChild>
              <Link to="/analysis">Вернуться к анализу</Link>
            </Button>
          </div>
        </main>
      </div>
    );
  }
  
  // Функция для получения иконки по типу фрукта
  const getFruitIcon = () => {
    const mainFruit = result.detected_fruits?.[0]?.fruit_type || 'apple';
    switch (mainFruit.toLowerCase()) {
      case 'apple': return '🍎';
      case 'pear': return '🍐';
      case 'cherry': return '🍒';
      case 'plum': return '🟣';
      default: return '🍎';
    }
  };
  
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
            Время обработки: {result.processing_time.toFixed(2)} секунды | 
            Точность: {Math.round(result.confidence * 100)}%
          </p>
        </div>
        
        <div className="grid grid-cols-2 gap-8 mb-8">
          {/* Image with Markup */}
          <Card>
            <CardContent className="pt-6">
              <div className="aspect-video bg-muted rounded-lg overflow-hidden mb-4 flex items-center justify-center">
                <div className="text-center p-8">
                  <div className="text-6xl mb-4">{getFruitIcon()}</div>
                  <p>Изображение с детекцией плодов</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    {result.detected_fruits?.length || 0} типов плодов обнаружено
                  </p>
                </div>
              </div>
              <div className="space-y-2">
                <h3 className="font-semibold">Обнаруженные плоды:</h3>
                {result.detected_fruits?.map((fruit, index) => (
                  <div key={index} className="flex justify-between items-center p-2 bg-secondary/20 rounded">
                    <span className="capitalize">{fruit.fruit_type}</span>
                    <span className="font-semibold">
                      {fruit.count} шт. ({Math.round(fruit.confidence * 100)}%)
                    </span>
                  </div>
                ))}
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
                  <span className="text-3xl">{getFruitIcon()}</span>
                  <div>
                    <p className="text-muted-foreground">Обнаружено плодов:</p>
                    <p className="text-3xl text-primary">{result.fruit_count}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                  <span className="text-2xl">🎯</span>
                  <div>
                    <p className="text-muted-foreground">Точность анализа:</p>
                    <p className="text-xl">
                      {Math.round(result.confidence * 100)}%
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                  <span className="text-2xl">⚡</span>
                  <div>
                    <p className="text-muted-foreground">Время обработки:</p>
                    <p className="text-xl">
                      {result.processing_time.toFixed(2)} сек
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                  <span className="text-2xl">🧠</span>
                  <div>
                    <p className="text-muted-foreground">Метод анализа:</p>
                    <p className="text-xl capitalize">{result.method}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                  <span className="text-2xl">📝</span>
                  <div>
                    <p className="text-muted-foreground">ID записи:</p>
                    <p className="text-xl">#{result.record_id}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* AI Comment */}
        {result.recommendations && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">📝</span>
              <h2 className="text-2xl">КОММЕНТАРИЙ ИИ:</h2>
            </div>
            
            <Card className="bg-secondary/10">
              <CardContent className="pt-6">
                <p className="text-lg">{result.recommendations}</p>
              </CardContent>
            </Card>
          </div>
        )}
        
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
      </main>
    </div>
  );
}