import { render, screen, waitFor } from '@testing-library/react';
import { useAuth } from '@clerk/clerk-react';
import OverviewPage from '../pages/dashboard/OverviewPage';
import { apiFetch } from '../lib/api';

jest.mock('@clerk/clerk-react', () => ({
  useAuth: jest.fn()
}));

jest.mock('../lib/api', () => ({
  apiFetch: jest.fn()
}));

test('shows loading state initially', async () => {
  useAuth.mockReturnValue({ getToken: jest.fn() });
  apiFetch.mockResolvedValue({ total_leads: 10, qualified: 5, booked: 3, conversion_rate: 30 });
  
  render(<OverviewPage />);
  
  expect(screen.getByText('Loading...')).toBeInTheDocument();
  
  await waitFor(() => {
    expect(screen.getByText('10')).toBeInTheDocument();
  });
});

test('shows stats after loading', async () => {
  useAuth.mockReturnValue({ getToken: jest.fn() });
  apiFetch.mockResolvedValue({ total_leads: 10, qualified: 5, booked: 3, conversion_rate: 30 });
  
  render(<OverviewPage />);
  
  await waitFor(() => {
    expect(screen.getByText('10')).toBeInTheDocument();
  });
});