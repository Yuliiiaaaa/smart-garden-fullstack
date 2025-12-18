// src/components/AuthPage.tsx (обновленный)
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Leaf } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { authService } from '../services/authService';
import { setAuthToken } from '../services/apiConfig';
import { useApiRequest } from '../hooks/useApiRequest';

export function AuthPage() {
  const navigate = useNavigate();
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [registerFullName, setRegisterFullName] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerConfirmPassword, setRegisterConfirmPassword] = useState('');
  
  const loginRequest = useApiRequest<any>();
  const registerRequest = useApiRequest<any>();
  
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!loginEmail || !loginPassword) {
      loginRequest.execute(() => Promise.reject(new Error('Заполните все поля')));
      return;
    }
    
    try {
      const result = await loginRequest.execute(() => 
        authService.login(loginEmail, loginPassword)
      );
      
      // Сохраняем токен
      setAuthToken(result.access_token);
      
      // Сохраняем пользователя в localStorage
      localStorage.setItem('user', JSON.stringify(result.user));
      
      console.log('Login successful, token saved:', result.access_token.substring(0, 20) + '...');
      console.log('User data:', result.user);
      
      navigate('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
    }
  };
  
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!registerFullName || !registerEmail || !registerPassword) {
      registerRequest.execute(() => Promise.reject(new Error('Заполните все обязательные поля')));
      return;
    }
    
    if (registerPassword !== registerConfirmPassword) {
      registerRequest.execute(() => Promise.reject(new Error('Пароли не совпадают')));
      return;
    }
    
    try {
      const user = await registerRequest.execute(() =>
        authService.register(registerEmail, registerPassword, registerFullName)
      );
      
      // После регистрации автоматически логинимся
      const loginResult = await authService.login(registerEmail, registerPassword);
      setAuthToken(loginResult.access_token);
      localStorage.setItem('user', JSON.stringify(loginResult.user));
      navigate('/dashboard');
    } catch (error) {
      // Ошибка уже обработана в useApiRequest
    }
  };
  
  const isLoading = loginRequest.loading || registerRequest.loading;
  const error = loginRequest.error || registerRequest.error;
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary/20 via-background to-primary/10 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <Link to="/" className="flex items-center gap-2 justify-center mb-8 hover:scale-105 transition-transform">
          <div className="p-2 bg-primary/10 rounded-full">
            <Leaf className="size-10 text-primary" />
          </div>
          <span className="text-2xl text-primary">Умный Сад</span>
        </Link>
        
        {/* Отображение ошибок */}
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}
        
        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Войти</TabsTrigger>
            <TabsTrigger value="register">Зарегистрироваться</TabsTrigger>
          </TabsList>
          
          <TabsContent value="login">
            <Card className="shadow-xl border-border/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Вход в систему</CardTitle>
                <CardDescription>
                  Введите свой email и пароль для входа
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email">Email</Label>
                    <Input
                      id="login-email"
                      type="email"
                      placeholder="example@mail.com"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      required
                      disabled={isLoading}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="login-password">Пароль</Label>
                    <Input
                      id="login-password"
                      type="password"
                      placeholder="••••••••"
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      required
                      disabled={isLoading}
                    />
                  </div>
                  
                  <Button 
                    type="submit" 
                    className="w-full"
                    disabled={isLoading}
                  >
                    {loginRequest.loading ? 'Вход...' : 'Войти'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="register">
            <Card className="shadow-xl border-border/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Создать аккаунт</CardTitle>
                <CardDescription>
                  Заполните форму для регистрации
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleRegister} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="register-fullname">ФИО</Label>
                    <Input
                      id="register-fullname"
                      type="text"
                      placeholder=" "
                      value={registerFullName}
                      onChange={(e) => setRegisterFullName(e.target.value)}
                      required
                      disabled={isLoading}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="register-email">Email</Label>
                    <Input
                      id="register-email"
                      type="email"
                      placeholder="example@mail.com"
                      value={registerEmail}
                      onChange={(e) => setRegisterEmail(e.target.value)}
                      required
                      disabled={isLoading}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="register-password">Пароль</Label>
                    <Input
                      id="register-password"
                      type="password"
                      placeholder="••••••••"
                      value={registerPassword}
                      onChange={(e) => setRegisterPassword(e.target.value)}
                      required
                      disabled={isLoading}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="register-password-confirm">Подтвердите пароль</Label>
                    <Input
                      id="register-password-confirm"
                      type="password"
                      placeholder="••••••••"
                      value={registerConfirmPassword}
                      onChange={(e) => setRegisterConfirmPassword(e.target.value)}
                      required
                      disabled={isLoading}
                    />
                  </div>
                  
                  <Button 
                    type="submit" 
                    className="w-full"
                    disabled={isLoading}
                  >
                    {registerRequest.loading ? 'Регистрация...' : 'Зарегистрироваться'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
        
        <div className="text-center mt-6">
          <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
            Вернуться на главную
          </Link>
        </div>
      </div>
    </div>
  );
}