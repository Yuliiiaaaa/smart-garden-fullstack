import { Download, FileSpreadsheet, RefreshCw } from 'lucide-react';
import { Header } from './Header';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const weeklyData = [
  { week: 'Неделя 1', count: 350 },
  { week: 'Неделя 2', count: 415 },
  { week: 'Неделя 3', count: 485 },
  { week: 'Неделя 4', count: 600 },
];

const treeData = [
  { tree: '#45', count: 65 },
  { tree: '#12', count: 58 },
  { tree: '#78', count: 52 },
  { tree: '#23', count: 48 },
  { tree: '#91', count: 45 },
  { tree: '#34', count: 43 },
  { tree: '#56', count: 41 },
  { tree: '#67', count: 39 },
  { tree: '#89', count: 37 },
  { tree: '#15', count: 35 },
];

export function AnalyticsPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header isLoggedIn userName=" " />
      
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl mb-4 flex items-center gap-2">
            <span className="text-2xl">📈</span>
            АНАЛИТИКА УРОЖАЙНОСТИ
          </h1>
          
          <div className="flex gap-4">
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Период:</span>
              <Select defaultValue="sept2024">
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sept2024">Сентябрь 2024</SelectItem>
                  <SelectItem value="aug2024">Август 2024</SelectItem>
                  <SelectItem value="july2024">Июль 2024</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Сад:</span>
              <Select defaultValue="apple">
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="apple">Яблоневый</SelectItem>
                  <SelectItem value="pear">Грушевый</SelectItem>
                  <SelectItem value="cherry">Вишневый</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
        
        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-primary/10 to-secondary/20">
            <CardContent className="pt-6 text-center">
              <div className="text-4xl mb-2 text-primary">1,850</div>
              <p className="text-muted-foreground">всего плодов</p>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-primary/10 to-secondary/20">
            <CardContent className="pt-6 text-center">
              <div className="text-4xl mb-2 text-primary">+18%</div>
              <p className="text-muted-foreground">рост за неделю</p>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-primary/10 to-secondary/20">
            <CardContent className="pt-6 text-center">
              <div className="text-4xl mb-2 text-primary">94%</div>
              <p className="text-muted-foreground">точность ИИ</p>
            </CardContent>
          </Card>
        </div>
        
        {/* Weekly Dynamics Chart */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">📊</span>
            <h2 className="text-2xl">ДИНАМИКА ПО НЕДЕЛЯМ:</h2>
          </div>
          
          <Card>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
                  <XAxis dataKey="week" stroke="#757575" />
                  <YAxis stroke="#757575" />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#4CAF50" 
                    strokeWidth={3} 
                    dot={{ fill: '#4CAF50', r: 6 }} 
                  />
                </LineChart>
              </ResponsiveContainer>
              <div className="mt-4 text-center">
                <p className="text-muted-foreground">
                  Неделя 1: 350 плодов | Неделя 2: 415 | Неделя 3: 485 | Неделя 4: 600 (прогноз)
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Tree Comparison Chart */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">🌳</span>
            <h2 className="text-2xl">СРАВНЕНИЕ ДЕРЕВЬЕВ:</h2>
          </div>
          
          <Card>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={treeData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
                  <XAxis dataKey="tree" stroke="#757575" />
                  <YAxis stroke="#757575" />
                  <Tooltip />
                  <Bar dataKey="count" fill="#4CAF50" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 text-center">
                <p className="text-muted-foreground">
                  Топ 10 деревьев по урожайности
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Export Buttons */}
        <div className="flex gap-4 justify-center">
          <Button size="lg" className="flex items-center gap-2">
            <Download className="size-5" />
            СКАЧАТЬ PDF-ОТЧЕТ
          </Button>
          <Button size="lg" variant="outline" className="flex items-center gap-2">
            <FileSpreadsheet className="size-5" />
            ЭКСПОРТ В EXCEL
          </Button>
          <Button size="lg" variant="outline" className="flex items-center gap-2">
            <RefreshCw className="size-5" />
            ОБНОВИТЬ
          </Button>
        </div>
      </main>
    </div>
  );
}