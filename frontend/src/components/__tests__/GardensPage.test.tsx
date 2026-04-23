// import { describe, it, expect, vi } from 'vitest';
// import { render, screen, fireEvent, waitFor } from '@testing-library/react';
// import { BrowserRouter } from 'react-router-dom';
// import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { GardensPage } from '../GardensPage';
// import { gardenService } from '../../services/gardenService';

// vi.mock('../../services/gardenService');

// const queryClient = new QueryClient({
//   defaultOptions: { queries: { retry: false } },
// });

// const renderWithClient = (ui: React.ReactElement) => {
//   return render(
//     <QueryClientProvider client={queryClient}>
//       <BrowserRouter>{ui}</BrowserRouter>
//     </QueryClientProvider>
//   );
// };

// describe('GardensPage', () => {
//   it('displays loading state initially', () => {
//     gardenService.getAllGardens = vi.fn().mockImplementation(() => new Promise(() => {}));
//     renderWithClient(<GardensPage />);
//     expect(screen.getByText(/Загрузка/i)).toBeInTheDocument();
//   });

//   it('displays gardens after loading', async () => {
//     const mockGardens = [
//       { id: 1, name: 'Apple Garden', fruit_type: 'apple', area: 2, location: 'North' },
//       { id: 2, name: 'Pear Garden', fruit_type: 'pear', area: 3, location: 'South' }
//     ];
//     gardenService.getAllGardens = vi.fn().mockResolvedValue(mockGardens);
//     renderWithClient(<GardensPage />);
//     await waitFor(() => {
//       expect(screen.getByText('Apple Garden')).toBeInTheDocument();
//       expect(screen.getByText('Pear Garden')).toBeInTheDocument();
//     });
//   });

//   it('filters gardens by name', async () => {
//     const mockGardens = [
//       { id: 1, name: 'Apple Garden', fruit_type: 'apple', area: 2, location: 'North' },
//       { id: 2, name: 'Pear Garden', fruit_type: 'pear', area: 3, location: 'South' }
//     ];
//     gardenService.getAllGardens = vi.fn().mockResolvedValue(mockGardens);
//     renderWithClient(<GardensPage />);
//     await waitFor(() => {
//       expect(screen.getByText('Apple Garden')).toBeInTheDocument();
//     });
//     const filterInput = screen.getByPlaceholderText(/Название сада/i);
//     fireEvent.change(filterInput, { target: { value: 'Apple' } });
//     fireEvent.click(screen.getByRole('button', { name: /Применить/i }));
//     await waitFor(() => {
//       expect(screen.getByText('Apple Garden')).toBeInTheDocument();
//       expect(screen.queryByText('Pear Garden')).not.toBeInTheDocument();
//     });
//   });
// });