// src/components/AnalysisPage.tsx (обновленный)
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Info, Loader2 } from 'lucide-react';
import { Header } from './Header';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Label } from './ui/label';
import { analysisService } from '../services/analysisService';
import { gardenService } from '../services/gardenService';
import { useApiRequest } from '../hooks/useApiRequest';
import { AnalysisResult } from '../services/apiConfig';

interface Garden {
  id: number;
  name: string;
  fruit_type: string;
}

export function AnalysisPage() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFruitType, setSelectedFruitType] = useState('apple');
  const [selectedScale, setSelectedScale] = useState('single');
  const [selectedGarden, setSelectedGarden] = useState<string>('');
  const [selectedTree, setSelectedTree] = useState('auto');
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  
  const analysisRequest = useApiRequest<AnalysisResult>();
  const gardensRequest = useApiRequest<Garden[]>();
  
  // Загрузка садов при монтировании
  useEffect(() => {
    loadGardens();
  }, []);
  
  // Создание preview при выборе файла
  useEffect(() => {
    if (!selectedFile) {
      setPreviewUrl('');
      return;
    }
    
    const objectUrl = URL.createObjectURL(selectedFile);
    setPreviewUrl(objectUrl);
    
    return () => URL.revokeObjectURL(objectUrl);
  }, [selectedFile]);
  
  const loadGardens = async () => {
    try {
      const data = await gardensRequest.execute(() => 
        gardenService.getAllGardens()
      );
      setGardens(data);
      if (data.length > 0) {
        setSelectedGarden(data[0].id.toString());
      }
    } catch (error) {
      console.error('Ошибка загрузки садов:', error);
    }
  };
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      
      // Проверка размера файла (макс 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('Файл слишком большой. Максимальный размер: 10MB');
        return;
      }
      
      // Проверка типа файла
      if (!file.type.match('image/jpeg') && !file.type.match('image/png')) {
        alert('Пожалуйста, загрузите изображение в формате JPG или PNG');
        return;
      }
      
      setSelectedFile(file);
    }
  };
  
  const handleAnalysis = async () => {
    if (!selectedFile) {
      alert('Пожалуйста, выберите файл для анализа');
      return;
    }
    
    try {
      const result = await analysisRequest.execute(() =>
        analysisService.analyzePhoto({
          file: selectedFile,
          fruit_type: selectedFruitType,
          tree_id: selectedTree !== 'auto' ? parseInt(selectedTree) : undefined,
          garden_id: selectedGarden ? parseInt(selectedGarden) : undefined,
        })
      );
      
      // Переходим на страницу результатов с данными
      navigate('/results', { state: { analysisResult: result } });
    } catch (error) {
      console.error('Ошибка анализа:', error);
    }
  };
  
  const isLoading = analysisRequest.loading || gardensRequest.loading;
  
  return (
    <div className="min-h-screen bg-background">
      <Header isLoggedIn userName="Иван" />
      
      <main className="container mx-auto px-6 py-8 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl mb-2 flex items-center gap-2">
            <span className="text-2xl">📸</span>
            АНАЛИЗ УРОЖАЯ
          </h1>
          {analysisRequest.error && (
            <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg mt-2">
              {analysisRequest.error}
            </div>
          )}
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
                disabled={isLoading}
              />
              <div className={`border-2 ${selectedFile ? 'border-primary' : 'border-dashed border-border'} rounded-lg p-8 text-center cursor-pointer hover:border-primary transition-colors ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}>
                {previewUrl ? (
                  <div className="mb-4">
                    <img 
                      src={previewUrl} 
                      alt="Preview" 
                      className="max-h-64 mx-auto rounded-lg object-contain"
                    />
                  </div>
                ) : (
                  <Upload className="size-16 mx-auto mb-4 text-muted-foreground" />
                )}
                <p className="text-xl mb-2">
                  {selectedFile 
                    ? selectedFile.name 
                    : 'Нажмите для выбора фотографии'}
                </p>
                <p className="text-muted-foreground">
                  Форматы: JPG, PNG, до 10MB
                </p>
                {selectedFile && (
                  <p className="text-sm text-muted-foreground mt-2">
                    Размер: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                )}
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
                <Select 
                  value={selectedFruitType} 
                  onValueChange={setSelectedFruitType}
                  disabled={isLoading}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="apple">Яблоки</SelectItem>
                    <SelectItem value="pear">Груши</SelectItem>
                    <SelectItem value="cherry">Вишни</SelectItem>
                    <SelectItem value="plum">Сливы</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="flex items-center gap-2 mb-2">
                  <span className="text-xl">🌳</span>
                  Масштаб:
                </Label>
                <Select 
                  value={selectedScale} 
                  onValueChange={setSelectedScale}
                  disabled={isLoading}
                >
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
                <Select 
                  value={selectedGarden} 
                  onValueChange={setSelectedGarden}
                  disabled={isLoading || gardensRequest.loading}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {gardensRequest.loading ? (
                      <SelectItem value="loading" disabled>
                        Загрузка садов...
                      </SelectItem>
                    ) : gardens.length === 0 ? (
                      <SelectItem value="none" disabled>
                        Нет доступных садов
                      </SelectItem>
                    ) : (
                      gardens.map((garden) => (
                        <SelectItem key={garden.id} value={garden.id.toString()}>
                          {garden.name}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="flex items-center gap-2 mb-2">
                  <span className="text-xl">🏷</span>
                  Дерево:
                </Label>
                <Select 
                  value={selectedTree} 
                  onValueChange={setSelectedTree}
                  disabled={isLoading}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto">Авто-определение</SelectItem>
                    <SelectItem value="15">Дерево #15</SelectItem>
                    <SelectItem value="45">Дерево #45</SelectItem>
                    <SelectItem value="78">Дерево #78</SelectItem>
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
            disabled={!selectedFile || isLoading}
            className="px-12 min-w-[200px]"
          >
            {analysisRequest.loading ? (
              <>
                <Loader2 className="mr-2 size-5 animate-spin" />
                АНАЛИЗ...
              </>
            ) : (
              '🔍 НАЧАТЬ АНАЛИЗ'
            )}
          </Button>
          
          {analysisRequest.loading && (
            <p className="text-muted-foreground mt-2">
              Обработка изображения... Это может занять несколько секунд
            </p>
          )}
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