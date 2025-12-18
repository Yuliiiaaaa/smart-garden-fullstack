import { Header } from './Header';
import { Card, CardContent } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { ImageWithFallback } from './figma/ImageWithFallback';

const historyData = [
  {
    date: '28.09.2024',
    garden: 'Яблоневый сад',
    location: 'Дерево #45',
    icon: '🍎',
    count: 52,
    fruit: 'яблока',
    accuracy: 96,
    time: '2.8s',
    size: '6.3см',
    image: 'https://images.unsplash.com/photo-1694132149888-8bd893e3029b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhcHBsZSUyMHRyZWUlMjBmcnVpdHN8ZW58MXx8fHwxNzU5MzI4NjczfDA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    date: '25.09.2024',
    garden: 'Яблоневый сад',
    location: 'Ряд 1-10',
    icon: '🍎',
    count: 425,
    fruit: 'яблок',
    accuracy: 94,
    time: '4.1s',
    size: '6.1см',
    image: 'https://images.unsplash.com/photo-1620969499889-3c9ceaed5fc8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxvcmNoYXJkJTIwYXBwbGUlMjBoYXJ2ZXN0fGVufDF8fHx8MTc1OTMyODcyNHww&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    date: '21.09.2024',
    garden: 'Грушевый сад',
    location: 'Дерево #8',
    icon: '🍐',
    count: 38,
    fruit: 'груш',
    accuracy: 92,
    time: '3.2s',
    size: '5.8см',
    image: 'https://images.unsplash.com/photo-1688539986327-ed9ccb94d39b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwZWFyJTIwdHJlZSUyMGZydWl0c3xlbnwxfHx8fDE3NTkzMjg3Mjh8MA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    date: '18.09.2024',
    garden: 'Яблоневый сад',
    location: 'Дерево #12',
    icon: '🍎',
    count: 45,
    fruit: 'яблок',
    accuracy: 95,
    time: '2.9s',
    size: '6.4см',
    image: 'https://images.unsplash.com/photo-1694132149888-8bd893e3029b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhcHBsZSUyMHRyZWUlMjBmcnVpdHN8ZW58MXx8fHwxNzU5MzI4NjczfDA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    date: '15.09.2024',
    garden: 'Вишневый сад',
    location: 'Дерево #3',
    icon: '🍒',
    count: 128,
    fruit: 'вишен',
    accuracy: 91,
    time: '3.5s',
    size: '2.1см',
    image: 'https://images.unsplash.com/photo-1694132149888-8bd893e3029b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhcHBsZSUyMHRyZWUlMjBmcnVpdHN8ZW58MXx8fHwxNzU5MzI4NjczfDA&ixlib=rb-4.1.0&q=80&w=1080',
  },
];

export function HistoryPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header isLoggedIn userName=" " />
      
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl mb-4 flex items-center gap-2">
            <span className="text-2xl">📋</span>
            ИСТОРИЯ АНАЛИЗОВ
          </h1>
          
          <div className="flex gap-4">
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Фильтры:</span>
              <Select defaultValue="all">
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все сады</SelectItem>
                  <SelectItem value="apple">Яблоневый</SelectItem>
                  <SelectItem value="pear">Грушевый</SelectItem>
                  <SelectItem value="cherry">Вишневый</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
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
            
            <Select defaultValue="apples">
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="apples">🍎 Яблоки</SelectItem>
                <SelectItem value="pears">🍐 Груши</SelectItem>
                <SelectItem value="cherries">🍒 Вишни</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        
        {/* History List */}
        <div className="space-y-4 mb-8">
          {historyData.map((item, index) => (
            <Card key={index} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex gap-6">
                  {/* Thumbnail */}
                  <div className="w-48 h-32 flex-shrink-0">
                    <ImageWithFallback
                      src={item.image}
                      alt={`${item.garden} ${item.location}`}
                      className="size-full object-cover rounded-lg"
                    />
                  </div>
                  
                  {/* Details */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xl">📅</span>
                          <span className="text-muted-foreground">{item.date}</span>
                          <span className="mx-2">|</span>
                          <span className="text-xl">{item.icon}</span>
                          <span>{item.garden}</span>
                          <span className="mx-2">|</span>
                          <span>{item.location}</span>
                        </div>
                        
                        <div className="flex items-center gap-6">
                          <div className="flex items-center gap-2">
                            <span className="text-xl">🎯</span>
                            <span className="text-primary text-xl">{item.count} {item.fruit}</span>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <span className="text-xl">✅</span>
                            <span>{item.accuracy}% точность</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-6 text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <span>⏱</span>
                        <span>{item.time}</span>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <span>📏</span>
                        <span>{item.size} средний размер</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        {/* Pagination */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <button className="px-4 py-2 rounded-lg bg-primary text-primary-foreground">1</button>
          <button className="px-4 py-2 rounded-lg hover:bg-muted transition-colors">2</button>
          <button className="px-4 py-2 rounded-lg hover:bg-muted transition-colors">3</button>
          <span className="px-4 py-2">...</span>
          <button className="px-4 py-2 rounded-lg hover:bg-muted transition-colors">12</button>
          <button className="px-4 py-2 rounded-lg hover:bg-muted transition-colors">{'>'}</button>
        </div>
        
        {/* Statistics Summary */}
        <Card className="bg-secondary/10">
          <CardContent className="pt-6 text-center">
            <p className="text-lg">
              Статистика: <span className="text-primary">128 анализов</span> | <span className="text-primary">95%</span> средняя точность
            </p>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}