import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Info } from 'lucide-react';
import { Header } from './Header';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Label } from './ui/label';

export function AnalysisPage() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };
  
  const handleAnalysis = () => {
    setIsAnalyzing(true);
    // Simulate AI analysis
    setTimeout(() => {
      navigate('/results');
    }, 3000);
  };
  
  return (
    <div className="min-h-screen bg-background">
      <Header isLoggedIn userName="Иван" />
      
      <main className="container mx-auto px-6 py-8 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl mb-2 flex items-center gap-2">
            <span className="text-2xl">📸</span>
            АНАЛИЗ УРОЖАЯ
          </h1>
        </div>
        
        {/* File Upload Area */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <label className="block">
              <input
                type="file"
                accept="image/jpeg,image/png"
                onChange={handleFileChange}
                className="hidden"
                disabled={isAnalyzing}
              />
              <div className="border-2 border-dashed border-border rounded-lg p-16 text-center cursor-pointer hover:border-primary transition-colors">
                <Upload className="size-16 mx-auto mb-4 text-muted-foreground" />
                <p className="text-xl mb-2">
                  {selectedFile ? selectedFile.name : 'Перетащите фото или нажмите для выбора'}
                </p>
                <p className="text-muted-foreground">
                  Форматы: JPG, PNG, до 10MB
                </p>
              </div>
            </label>
          </CardContent>
        </Card>
        
        {/* Analysis Settings */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">⚙</span>
            <h2 className="text-2xl">НАСТРОЙКИ АНАЛИЗА:</h2>
          </div>
          
          <Card>
            <CardContent className="pt-6 space-y-4">
              <div>
                <Label className="flex items-center gap-2 mb-2">
                  <span className="text-xl">🍎</span>
                  Тип плодов:
                </Label>
                <Select defaultValue="apples">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="apples">Яблоки</SelectItem>
                    <SelectItem value="pears">Груши</SelectItem>
                    <SelectItem value="cherries">Вишни</SelectItem>
                    <SelectItem value="plums">Сливы</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="flex items-center gap-2 mb-2">
                  <span className="text-xl">🌳</span>
                  Масштаб:
                </Label>
                <Select defaultValue="single">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="single">Отдельное дерево</SelectItem>
                    <SelectItem value="row">Ряд деревьев</SelectItem>
                    <SelectItem value="section">Секция сада</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="flex items-center gap-2 mb-2">
                  <span className="text-xl">📍</span>
                  Сад:
                </Label>
                <Select defaultValue="apple">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="apple">Яблоневый сад</SelectItem>
                    <SelectItem value="pear">Грушевый сад</SelectItem>
                    <SelectItem value="cherry">Вишневый сад</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="flex items-center gap-2 mb-2">
                  <span className="text-xl">🏷</span>
                  Дерево:
                </Label>
                <Select defaultValue="auto">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto">Авто-определение</SelectItem>
                    <SelectItem value="tree15">Дерево #15</SelectItem>
                    <SelectItem value="tree45">Дерево #45</SelectItem>
                    <SelectItem value="tree78">Дерево #78</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Analysis Button */}
        <div className="mb-8 text-center">
          <Button 
            size="lg" 
            onClick={handleAnalysis}
            disabled={!selectedFile || isAnalyzing}
            className="px-12"
          >
            {isAnalyzing ? 'АНАЛИЗ...' : '🔍 НАЧАТЬ АНАЛИЗ'}
          </Button>
        </div>
        
        {/* Tips */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">💡</span>
            <h2 className="text-2xl">СОВЕТЫ ДЛЯ ЛУЧШЕГО АНАЛИЗА:</h2>
          </div>
          
          <Card className="bg-secondary/10">
            <CardContent className="pt-6">
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span>•</span>
                  <span>Снимайте при хорошем освещении</span>
                </li>
                <li className="flex items-start gap-2">
                  <span>•</span>
                  <span>Фотографируйте с расстояния 2-3 метра</span>
                </li>
                <li className="flex items-start gap-2">
                  <span>•</span>
                  <span>Избегайте бликов и теней</span>
                </li>
                <li className="flex items-start gap-2">
                  <span>•</span>
                  <span>Показывайте всю крону дерева</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}