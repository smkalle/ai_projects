
import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  TextField,
  InputAdornment,
  Grid,
  Paper,
  Alert,
  Skeleton
} from '@mui/material';
import { Search, TrendingDown, TrendingUp } from '@mui/icons-material';
import { useQuery } from 'react-query';

interface PriceData {
  product: string;
  farmer_price: number;
  bigbasket_price: number;
  zepto_price: number;
  swiggy_price: number;
  farmer_savings: number;
  trend: 'up' | 'down' | 'stable';
}

const PriceComparison: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const { data: priceData, isLoading, error } = useQuery<PriceData[]>(
    'price-comparison',
    async () => {
      const response = await fetch('/api/price-comparison');
      if (!response.ok) throw new Error('Failed to fetch price data');
      return response.json();
    },
    {
      refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    }
  );

  const filteredData = priceData?.filter(item =>
    item.product.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const totalSavings = filteredData.reduce((sum, item) => sum + item.farmer_savings, 0);

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="error">
          Failed to load price comparison data. Please try again later.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Live Price Comparison
      </Typography>

      <Typography variant="subtitle1" color="text.secondary" align="center" sx={{ mb: 4 }}>
        Compare prices between direct farmers and major retail platforms
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(45deg, #4CAF50, #66BB6A)' }}>
            <CardContent>
              <Typography variant="h6" color="white">
                Total Potential Savings
              </Typography>
              <Typography variant="h4" color="white">
                ₹{totalSavings}
              </Typography>
              <Typography variant="body2" color="white">
                Per basket on selected items
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(45deg, #2196F3, #42A5F5)' }}>
            <CardContent>
              <Typography variant="h6" color="white">
                Average Savings
              </Typography>
              <Typography variant="h4" color="white">
                32%
              </Typography>
              <Typography variant="body2" color="white">
                Compared to retail platforms
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(45deg, #FF9800, #FFB74D)' }}>
            <CardContent>
              <Typography variant="h6" color="white">
                Products Tracked
              </Typography>
              <Typography variant="h4" color="white">
                {filteredData.length}
              </Typography>
              <Typography variant="body2" color="white">
                Updated every 5 minutes
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search */}
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search products..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search />
            </InputAdornment>
          ),
        }}
        sx={{ mb: 3 }}
      />

      {/* Price Comparison Table */}
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Product</TableCell>
                <TableCell align="right">Direct Farmer</TableCell>
                <TableCell align="right">BigBasket</TableCell>
                <TableCell align="right">Zepto</TableCell>
                <TableCell align="right">Swiggy</TableCell>
                <TableCell align="right">Your Savings</TableCell>
                <TableCell align="right">Trend</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, index) => (
                  <TableRow key={index}>
                    {Array.from({ length: 7 }).map((_, cellIndex) => (
                      <TableCell key={cellIndex}>
                        <Skeleton variant="text" />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                filteredData.map((row, index) => (
                  <TableRow key={index} hover>
                    <TableCell component="th" scope="row">
                      <Typography variant="subtitle2">
                        {row.product}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="h6" color="primary">
                        ₹{row.farmer_price}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">₹{row.bigbasket_price}</TableCell>
                    <TableCell align="right">₹{row.zepto_price}</TableCell>
                    <TableCell align="right">₹{row.swiggy_price}</TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`₹${row.farmer_savings}`}
                        color="success"
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {row.trend === 'up' && <TrendingUp color="success" />}
                      {row.trend === 'down' && <TrendingDown color="error" />}
                      {row.trend === 'stable' && <Typography>-</Typography>}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Box sx={{ mt: 3 }}>
        <Typography variant="caption" color="text.secondary">
          * Prices are updated every 5 minutes through automated scraping
        </Typography>
      </Box>
    </Container>
  );
};

export default PriceComparison;
