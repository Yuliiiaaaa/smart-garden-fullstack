import { Link, useLocation } from 'react-router-dom';
import { Leaf, User } from 'lucide-react';
import { Button } from './ui/button';

interface HeaderProps {
  isLoggedIn?: boolean;
  userName?: string;
}

export function Header({ isLoggedIn = false, userName }: HeaderProps) {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <header className="border-b bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4 flex items-center justify-between max-w-7xl">
        <Link to="/" className="flex items-center gap-2 hover:scale-105 transition-transform">
          <div className="p-1.5 bg-primary/10 rounded-full">
            <Leaf className="size-8 text-primary" />
          </div>
          <span className="text-xl text-primary">Умный Сад</span>
        </Link>
        
        <nav className="flex items-center gap-6">
          {isLoggedIn ? (
            <>
              <Link 
                to="/dashboard" 
                className={`transition-colors ${isActive('/dashboard') ? 'text-primary' : 'text-muted-foreground hover:text-primary'}`}
              >
                Дашборд
              </Link>
              <Link 
                to="/analysis" 
                className={`transition-colors ${isActive('/analysis') ? 'text-primary' : 'text-muted-foreground hover:text-primary'}`}
              >
                Анализ
              </Link>
              <Link 
                to="/history" 
                className={`transition-colors ${isActive('/history') ? 'text-primary' : 'text-muted-foreground hover:text-primary'}`}
              >
                История
              </Link>
              <Link 
                to="/analytics" 
                className={`transition-colors ${isActive('/analytics') ? 'text-primary' : 'text-muted-foreground hover:text-primary'}`}
              >
                Аналитика
              </Link>
              <div className="flex items-center gap-2 ml-4">
                <User className="size-5" />
                <span>{userName || 'Иван'}</span>
              </div>
            </>
          ) : (
            <>
              <Link 
                to="/" 
                className={`transition-colors ${isActive('/') ? 'text-primary' : 'text-muted-foreground hover:text-primary'}`}
              >
                Главная
              </Link>
              <Button asChild className="shadow-md hover:shadow-lg transition-all">
                <Link to="/auth">Зарегистрироваться</Link>
              </Button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}