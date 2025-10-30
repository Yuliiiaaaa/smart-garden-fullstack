import { Link } from 'react-router-dom';
import { Camera, FileText, TrendingUp } from 'lucide-react';
import { Header } from './Header';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const chartData = [
  { week: 'Нед 1', count: 120 },
  { week: 'Нед 2', count: 145 },
  { week: 'Нед 3', count: 168 },
  { week: 'Нед 4', count: 195 },
  { week: 'Нед 5', count: 210 },
  { week: 'Нед 6', count: 235 },
];

const recentAnalyses = [
  { time: 'Сегодня, 14:30', tree: 'Дерево #45', count: 52, fruit: 'яблок' },
  { time: 'Сегодня, 11:15', tree: 'Дерево #12', count: 38, fruit: 'яблок' },
  { time: 'Вчера, 16:20', tree: 'Дерево #78', count: 41, fruit: 'яблоко' },
  { time: '25.09, 09:45', tree: 'Ряд 1-10', count: 425, fruit: 'яблок' },
];

export function Dashboard() {
  return (
    <div className="min-h-screen bg-background">
      <Header isLoggedIn userName="Иван" />
      
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl mb-2">Добро пожаловать, Иван! 🍎</h1>
        </div>
        
        {/* Gardens Overview */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">📊</span>
            <h2 className="text-2xl">ОБЗОР ВАШИХ САДОВ:</h2>
          </div>
          
          <div className="grid grid-cols-3 gap-6">
            <Card className="border-2 hover:border-primary transition-colors cursor-pointer">
              <CardContent className="pt-6">
                <div className="text-4xl mb-2">🍎</div>
                <h3 className="mb-2">Яблоневый</h3>
                <p className="text-muted-foreground mb-1">150 деревьев</p>
                <div className="flex items-center gap-2">
                  <span className="text-primary">Урожай: 85%</span>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-2 hover:border-primary transition-colors cursor-pointer">
              <CardContent className="pt-6">
                <div className="text-4xl mb-2">🍐</div>
                <h3 className="mb-2">Грушевый</h3>
                <p className="text-muted-foreground mb-1">80 деревьев</p>
                <div className="flex items-center gap-2">
                  <span className="text-primary">Урожай: 60%</span>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-2 hover:border-primary transition-colors cursor-pointer">
              <CardContent className="pt-6">
                <div className="text-4xl mb-2">🍒</div>
                <h3 className="mb-2">Вишневый</h3>
                <p className="text-muted-foreground mb-1">45 деревьев</p>
                <div className="flex items-center gap-2">
                  <span className="text-primary">Урожай: 95%</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
        
        {/* Quick Actions */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">🎯</span>
            <h2 className="text-2xl">БЫСТРЫЕ ДЕЙСТВИЯ:</h2>
          </div>
          
          <div className="flex gap-4">
            <Button size="lg" asChild>
              <Link to="/analysis" className="flex items-center gap-2">
                <Camera className="size-5" />
                ЗАГРУЗИТЬ ФОТО ДЛЯ АНАЛИЗА
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/analytics" className="flex items-center gap-2">
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
            <h2 className="text-2xl">ДИНАМИКА УРОЖАЙНОСТИ (Яблоневый сад):</h2>
          </div>
          
          <Card>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
                  <XAxis dataKey="week" stroke="#757575" />
                  <YAxis stroke="#757575" />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#4CAF50" strokeWidth={3} dot={{ fill: '#4CAF50', r: 5 }} />
                </LineChart>
              </ResponsiveContainer>
              <p className="text-center text-muted-foreground mt-4">
                Сентябрь 2024 → Урожай растет на 18% в неделю
              </p>
            </CardContent>
          </Card>
        </div>
        
        {/* Recent Analyses */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">🗓</span>
            <h2 className="text-2xl">ПОСЛЕДНИЕ АНАЛИЗЫ:</h2>
          </div>
          
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                {recentAnalyses.map((analysis, index) => (
                  <div key={index} className="flex items-center justify-between py-3 border-b last:border-0">
                    <div className="flex items-center gap-4">
                      <span className="text-2xl">🕐</span>
                      <div>
                        <span className="text-muted-foreground">{analysis.time}</span>
                        <span className="mx-2">|</span>
                        <span>{analysis.tree}</span>
                        <span className="mx-2">→</span>
                        <span className="text-primary">{analysis.count} {analysis.fruit}</span>
                      </div>
                    </div>
                    <span className="text-2xl">✅</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}