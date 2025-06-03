# BudgetManager Pro - Frontend Context & Instructions

## Project Overview
BudgetManager Pro frontend is a modern React application with TypeScript that provides an intuitive, secure interface for personal finance management, transaction categorization, and budget tracking.

## Frontend Architecture

### Technology Stack
- **Framework**: React 18+
- **Language**: TypeScript 5+
- **Build Tool**: Vite 5+
- **Styling**: Tailwind CSS + Shadcn/UI components
- **State Management**: Zustand (lightweight, TypeScript-friendly)
- **HTTP Client**: Axios with interceptors
- **Routing**: React Router v6
- **Forms**: React Hook Form + Zod validation
- **Charts**: Recharts for financial visualizations
- **Location**: `src/frontend/`

### Project Structure
```
src/frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # Base UI components (shadcn/ui)
│   │   ├── forms/          # Form components
│   │   ├── charts/         # Chart components
│   │   └── layout/         # Layout components
│   ├── pages/              # Page components (routes)
│   │   ├── auth/           # Login, register, etc.
│   │   ├── dashboard/      # Main dashboard
│   │   ├── accounts/       # Account management
│   │   ├── transactions/   # Transaction views
│   │   ├── budgets/        # Budget management
│   │   └── settings/       # User settings
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API service layer
│   ├── stores/             # Zustand state management
│   ├── utils/              # Utility functions
│   ├── types/              # TypeScript type definitions
│   └── App.tsx             # Main application component
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

### Authentication & Security

#### JWT Token Management
```typescript
// Auth store with token management
interface AuthStore {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

// Axios interceptor for token attachment
axios.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

#### Protected Routes
```typescript
// Route protection component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// Router setup with protection
const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />
  },
  {
    path: "/",
    element: <ProtectedRoute><DashboardLayout /></ProtectedRoute>,
    children: [
      { path: "/", element: <DashboardPage /> },
      { path: "/accounts", element: <AccountsPage /> },
      { path: "/transactions", element: <TransactionsPage /> },
      { path: "/budgets", element: <BudgetsPage /> }
    ]
  }
]);
```

### State Management with Zustand

#### Account Store
```typescript
interface AccountStore {
  accounts: Account[];
  selectedAccount: Account | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchAccounts: () => Promise<void>;
  createAccount: (data: CreateAccountData) => Promise<void>;
  updateAccount: (id: number, data: UpdateAccountData) => Promise<void>;
  deleteAccount: (id: number) => Promise<void>;
  selectAccount: (account: Account) => void;
}

const useAccountStore = create<AccountStore>((set, get) => ({
  accounts: [],
  selectedAccount: null,
  loading: false,
  error: null,
  
  fetchAccounts: async () => {
    set({ loading: true, error: null });
    try {
      const accounts = await accountService.getAccounts();
      set({ accounts, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  }
}));
```

#### Transaction Store
```typescript
interface TransactionStore {
  transactions: Transaction[];
  filters: TransactionFilters;
  pagination: PaginationState;
  loading: boolean;
  
  // Actions
  fetchTransactions: () => Promise<void>;
  createTransaction: (data: CreateTransactionData) => Promise<void>;
  importTransactions: (file: File, accountId: number) => Promise<void>;
  categorizeTransaction: (id: number, categoryId: number) => Promise<void>;
  setFilters: (filters: Partial<TransactionFilters>) => void;
}
```

### Component Architecture

#### Dashboard Layout
```typescript
const DashboardLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="pl-64">
        <Header />
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
```

#### Account Management Components
```typescript
// Account list with filtering and actions
const AccountsList: React.FC = () => {
  const { accounts, loading, fetchAccounts } = useAccountStore();
  const [filters, setFilters] = useState<AccountFilters>({});
  
  useEffect(() => {
    fetchAccounts();
  }, []);
  
  return (
    <div className="space-y-4">
      <AccountFilters filters={filters} onChange={setFilters} />
      <AccountGrid accounts={filteredAccounts} />
      <CreateAccountDialog />
    </div>
  );
};

// Account card component
const AccountCard: React.FC<{ account: Account }> = ({ account }) => {
  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-semibold">{account.name}</h3>
          <p className="text-gray-600">{account.bank_name}</p>
          <p className="text-sm text-gray-500">{account.account_type}</p>
        </div>
        <div className="text-right">
          <p className="text-xl font-bold">${account.balance.toFixed(2)}</p>
          <AccountActions account={account} />
        </div>
      </div>
    </Card>
  );
};
```

### Transaction Management

#### Transaction Table with Filtering
```typescript
const TransactionTable: React.FC = () => {
  const { transactions, filters, pagination, setFilters } = useTransactionStore();
  
  return (
    <div className="space-y-4">
      <TransactionFilters 
        filters={filters} 
        onFiltersChange={setFilters}
      />
      
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Date</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Amount</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {transactions.map((transaction) => (
            <TransactionRow 
              key={transaction.id} 
              transaction={transaction}
            />
          ))}
        </TableBody>
      </Table>
      
      <Pagination 
        current={pagination.page}
        total={pagination.total}
        pageSize={pagination.size}
        onChange={(page) => setPagination({ ...pagination, page })}
      />
    </div>
  );
};
```

#### CSV Import Interface
```typescript
const CSVImportModal: React.FC<{ accountId: number; isOpen: boolean; onClose: () => void }> = ({
  accountId,
  isOpen,
  onClose
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [institution, setInstitution] = useState<string>('');
  const [preview, setPreview] = useState<TransactionPreview[]>([]);
  
  const handleFileUpload = async (uploadedFile: File) => {
    setFile(uploadedFile);
    try {
      const previewData = await csvService.previewImport(uploadedFile, institution);
      setPreview(previewData);
    } catch (error) {
      toast.error('Failed to preview file');
    }
  };
  
  const handleConfirmImport = async () => {
    if (!file) return;
    
    try {
      await csvService.confirmImport(file, accountId, institution);
      toast.success('Transactions imported successfully');
      onClose();
    } catch (error) {
      toast.error('Import failed');
    }
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Import Transactions</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <InstitutionSelector 
            value={institution}
            onChange={setInstitution}
          />
          
          <FileUpload 
            accept=".csv"
            onFileSelect={handleFileUpload}
          />
          
          {preview.length > 0 && (
            <ImportPreview 
              transactions={preview}
              onConfirm={handleConfirmImport}
            />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
```

### Budget Visualization

#### Budget Dashboard with Charts
```typescript
const BudgetDashboard: React.FC = () => {
  const { budgets, loading } = useBudgetStore();
  const { transactions } = useTransactionStore();
  
  const budgetData = useMemo(() => {
    return budgets.map(budget => ({
      ...budget,
      spent: calculateSpentAmount(transactions, budget),
      remaining: budget.amount - calculateSpentAmount(transactions, budget),
      percentageUsed: (calculateSpentAmount(transactions, budget) / budget.amount) * 100
    }));
  }, [budgets, transactions]);
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Budget Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={budgetData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="amount" fill="#8884d8" name="Budget" />
              <Bar dataKey="spent" fill="#82ca9d" name="Spent" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Spending by Category</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categorySpending}
                dataKey="amount"
                nameKey="category"
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                label
              />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};
```

### Form Handling with React Hook Form

#### Account Creation Form
```typescript
const CreateAccountForm: React.FC<{ onSuccess: () => void }> = ({ onSuccess }) => {
  const { createAccount } = useAccountStore();
  
  const form = useForm<CreateAccountFormData>({
    resolver: zodResolver(createAccountSchema),
    defaultValues: {
      name: '',
      account_type: 'checking',
      bank_name: '',
      initial_balance: 0
    }
  });
  
  const onSubmit = async (data: CreateAccountFormData) => {
    try {
      await createAccount(data);
      toast.success('Account created successfully');
      onSuccess();
    } catch (error) {
      toast.error('Failed to create account');
    }
  };
  
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Account Name</FormLabel>
              <FormControl>
                <Input placeholder="My Checking Account" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <FormField
          control={form.control}
          name="account_type"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Account Type</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select account type" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="checking">Checking</SelectItem>
                  <SelectItem value="savings">Savings</SelectItem>
                  <SelectItem value="credit_card">Credit Card</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <Button type="submit" className="w-full">
          Create Account
        </Button>
      </form>
    </Form>
  );
};
```

### API Service Layer

#### Account Service
```typescript
class AccountService {
  private api = axios.create({
    baseURL: '/api/v1/accounts'
  });
  
  async getAccounts(filters?: AccountFilters): Promise<Account[]> {
    const params = new URLSearchParams();
    if (filters?.account_type) params.append('account_type', filters.account_type);
    if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString());
    
    const response = await this.api.get(`/?${params.toString()}`);
    return response.data;
  }
  
  async createAccount(data: CreateAccountData): Promise<Account> {
    const response = await this.api.post('/', data);
    return response.data;
  }
  
  async updateAccount(id: number, data: UpdateAccountData): Promise<Account> {
    const response = await this.api.put(`/${id}`, data);
    return response.data;
  }
  
  async deleteAccount(id: number): Promise<void> {
    await this.api.delete(`/${id}`);
  }
}

export const accountService = new AccountService();
```

### Error Handling & User Feedback

#### Global Error Handler
```typescript
// Error boundary component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error: Error) {
    return { hasError: true };
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <Card className="p-6 text-center">
            <h2 className="text-xl font-semibold mb-2">Something went wrong</h2>
            <p className="text-gray-600 mb-4">
              We encountered an unexpected error. Please refresh the page.
            </p>
            <Button onClick={() => window.location.reload()}>
              Refresh Page
            </Button>
          </Card>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

#### Toast Notifications
```typescript
// Custom hook for notifications
const useNotifications = () => {
  const notify = {
    success: (message: string) => toast.success(message),
    error: (message: string) => toast.error(message),
    warning: (message: string) => toast.warning(message),
    info: (message: string) => toast.info(message)
  };
  
  return notify;
};
```

### Performance Optimization

#### Virtual Scrolling for Large Lists
```typescript
const VirtualizedTransactionList: React.FC<{ transactions: Transaction[] }> = ({ 
  transactions 
}) => {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: transactions.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 60,
    overscan: 10
  });
  
  return (
    <div ref={parentRef} className="h-96 overflow-auto">
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: virtualRow.size,
              transform: `translateY(${virtualRow.start}px)`
            }}
          >
            <TransactionRow transaction={transactions[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### Memoization for Expensive Calculations
```typescript
const BudgetCalculations: React.FC<{ transactions: Transaction[]; budgets: Budget[] }> = ({
  transactions,
  budgets
}) => {
  const budgetAnalysis = useMemo(() => {
    return budgets.map(budget => ({
      ...budget,
      spent: transactions
        .filter(t => t.category_id === budget.category_id)
        .reduce((sum, t) => sum + Math.abs(t.amount), 0),
      percentageUsed: calculateBudgetPercentage(transactions, budget)
    }));
  }, [transactions, budgets]);
  
  return <BudgetChart data={budgetAnalysis} />;
};
```

### Development Guidelines

#### TypeScript Best Practices
1. **Strict type checking** enabled in tsconfig.json
2. **Interface definitions** for all API responses
3. **Generic components** with proper type constraints
4. **Utility types** for form data and API requests
5. **Type guards** for runtime type validation

#### Component Design Principles
1. **Single responsibility** - each component has one job
2. **Composition over inheritance** - use composition patterns
3. **Props interface** - define clear prop interfaces
4. **Error boundaries** - wrap components with error handling
5. **Accessibility** - proper ARIA labels and keyboard navigation

#### State Management Best Practices
1. **Minimal state** - keep state as small as possible
2. **Derived state** - compute values from existing state
3. **Async handling** - proper loading and error states
4. **Optimistic updates** - update UI before API confirmation
5. **State normalization** - avoid nested state structures

### Testing Strategy

#### Component Testing
```typescript
// Example component test
describe('AccountCard', () => {
  it('renders account information correctly', () => {
    const mockAccount: Account = {
      id: 1,
      name: 'Test Account',
      balance: 1000,
      account_type: 'checking',
      bank_name: 'Test Bank'
    };
    
    render(<AccountCard account={mockAccount} />);
    
    expect(screen.getByText('Test Account')).toBeInTheDocument();
    expect(screen.getByText('$1000.00')).toBeInTheDocument();
    expect(screen.getByText('Test Bank')).toBeInTheDocument();
  });
});
```

#### Store Testing
```typescript
// Example store test
describe('AccountStore', () => {
  beforeEach(() => {
    useAccountStore.setState({
      accounts: [],
      loading: false,
      error: null
    });
  });
  
  it('fetches accounts successfully', async () => {
    const mockAccounts = [{ id: 1, name: 'Test Account' }];
    accountService.getAccounts = jest.fn().mockResolvedValue(mockAccounts);
    
    await useAccountStore.getState().fetchAccounts();
    
    expect(useAccountStore.getState().accounts).toEqual(mockAccounts);
    expect(useAccountStore.getState().loading).toBe(false);
  });
});
```

## Key Files to Focus On
- `src/frontend/src/App.tsx` - Main application setup
- `src/frontend/src/pages/` - Page components and routing
- `src/frontend/src/components/` - Reusable UI components
- `src/frontend/src/stores/` - State management
- `src/frontend/src/services/` - API service layer
- `src/frontend/src/types/` - TypeScript definitions
- `src/frontend/package.json` - Dependencies and scripts
- `src/frontend/vite.config.ts` - Build configuration
