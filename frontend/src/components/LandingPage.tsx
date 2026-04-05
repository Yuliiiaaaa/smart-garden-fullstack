// src/components/LandingPage.tsx
import { Link } from 'react-router-dom';
import { Camera, TrendingUp, BarChart3, Upload, Brain, FileText } from 'lucide-react';
import { Header } from './Header';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { SEO } from './SEO';   // импорт SEO-компонента

export function LandingPage() {
  return (
    <>
      {/* SEO-метатеги для главной страницы */}
      <SEO
        title="Главная"
        description="Smart Garden – автоматический подсчёт урожая с помощью искусственного интеллекта. Управляйте садами, анализируйте фотографии, получайте аналитику урожайности."
        canonical="/"
        ogImage="/og-image.jpg"   // поместите изображение в папку public
        ogType="website"
        noindex={false}           // страница индексируется
      />

      <div className="min-h-screen bg-gradient-to-br from-background via-secondary/5 to-primary/5">
        <Header isLoggedIn={false} />
        
        <main className="container mx-auto px-6 py-16 max-w-7xl">
          {/* Hero Section */}
          <div className="text-center mb-20">
            <div className="inline-flex items-center gap-2 bg-gradient-to-r from-secondary/40 to-primary/20 px-6 py-3 rounded-full mb-6 shadow-lg backdrop-blur-sm border border-primary/10">
              <span className="text-2xl"></span>
              <span className="text-muted-foreground">учёт урожая</span>
            </div>
          </div>
          
          {/* How It Works */}
          <div className="mb-20">
            <div className="flex items-center gap-2 mb-8">
              <span className="text-2xl"></span>
              <h2 className="text-3xl">КАК ЭТО РАБОТАЕТ:</h2>
            </div>
            
            <div className="grid grid-cols-3 gap-8">
              <Card className="border-2 shadow-lg hover:shadow-2xl transition-all hover:scale-105 hover:border-primary/30 bg-gradient-to-br from-card to-secondary/5">
                <CardContent className="pt-6 text-center">
                  <div className="size-16 rounded-full bg-gradient-to-br from-secondary/40 to-primary/20 flex items-center justify-center mx-auto mb-4 shadow-md">
                    <Upload className="size-8 text-primary" />
                  </div>
                  <h3 className="mb-2"> Фото</h3>
                  <p className="text-muted-foreground">Загрузите снимки</p>
                </CardContent>
              </Card>
              
              <Card className="border-2 shadow-lg hover:shadow-2xl transition-all hover:scale-105 hover:border-primary/30 bg-gradient-to-br from-card to-secondary/5">
                <CardContent className="pt-6 text-center">
                  <div className="size-16 rounded-full bg-gradient-to-br from-secondary/40 to-primary/20 flex items-center justify-center mx-auto mb-4 shadow-md">
                    <Brain className="size-8 text-primary" />
                  </div>
                  <h3 className="mb-2"> Анализ</h3>
                  <p className="text-muted-foreground">ИИ считает плоды</p>
                </CardContent>
              </Card>
              
              <Card className="border-2 shadow-lg hover:shadow-2xl transition-all hover:scale-105 hover:border-primary/30 bg-gradient-to-br from-card to-secondary/5">
                <CardContent className="pt-6 text-center">
                  <div className="size-16 rounded-full bg-gradient-to-br from-secondary/40 to-primary/20 flex items-center justify-center mx-auto mb-4 shadow-md">
                    <FileText className="size-8 text-primary" />
                  </div>
                  <h3 className="mb-2"> Отчет</h3>
                  <p className="text-muted-foreground">Смотрите графики</p>
                </CardContent>
              </Card>
            </div>
          </div>
          
          {/* Platform Statistics */}
          <div>
            <div className="flex items-center gap-2 mb-8">
              <span className="text-2xl"></span>
              <h2 className="text-3xl">СТАТИСТИКА ПЛАТФОРМЫ:</h2>
            </div>
            
            <div className="grid grid-cols-3 gap-8">
              <Card className="bg-gradient-to-br from-primary/10 to-secondary/20 border-primary/20 shadow-xl hover:shadow-2xl transition-all hover:scale-105">
                <CardContent className="pt-6 text-center">
                  <div className="text-4xl mb-2 text-primary">10,000+</div>
                  <p className="text-muted-foreground">обработанных изображений</p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-primary/10 to-secondary/20 border-primary/20 shadow-xl hover:shadow-2xl transition-all hover:scale-105">
                <CardContent className="pt-6 text-center">
                  <div className="text-4xl mb-2 text-primary">95%</div>
                  <p className="text-muted-foreground">точность подсчета</p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-primary/10 to-secondary/20 border-primary/20 shadow-xl hover:shadow-2xl transition-all hover:scale-105">
                <CardContent className="pt-6 text-center">
                  <div className="text-4xl mb-2 text-primary">50+</div>
                  <p className="text-muted-foreground">садов используют</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}