
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShoppingCart, Agriculture, LocalShipping, TrendingUp, Store, Eco } from '@mui/icons-material';

interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
  unit: string;
  farmer_name: string;
  location: string;
  organic_certified: boolean;
  description: string;
}

interface PriceComparison {
  product_name: string;
  farmer_price: number;
  bigbasket_price: number;
  zepto_price: number;
  swiggy_price: number;
  savings_percentage: number;
}

interface Stats {
  total_farmers: number;
  total_products: number;
  average_savings: string;
  active_users: number;
  orders_today: number;
  revenue_today: string;
}

const App: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [priceComparison, setPriceComparison] = useState<PriceComparison[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [activeTab, setActiveTab] = useState('products');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [productsRes, priceRes, statsRes] = await Promise.all([
        axios.get('http://localhost:8000/api/products'),
        axios.get('http://localhost:8000/api/price-comparison'),
        axios.get('http://localhost:8000/api/stats')
      ]);
      setProducts(productsRes.data);
      setPriceComparison(priceRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Agriculture className="text-green-600" style={{ fontSize: 40 }} />
              <h1 className="text-3xl font-bold text-gray-800">FarmConnect</h1>
            </div>
            <p className="text-gray-600">Direct from Farm to Your Table</p>
          </div>
        </div>
      </header>

      {/* Stats Dashboard */}
      {stats && (
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-2xl font-bold text-green-600">{stats.total_farmers}</div>
              <div className="text-sm text-gray-600">Active Farmers</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-2xl font-bold text-blue-600">{stats.total_products}</div>
              <div className="text-sm text-gray-600">Products</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-2xl font-bold text-orange-600">{stats.average_savings}</div>
              <div className="text-sm text-gray-600">Avg Savings</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-2xl font-bold text-purple-600">{stats.active_users}</div>
              <div className="text-sm text-gray-600">Active Users</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-2xl font-bold text-red-600">{stats.orders_today}</div>
              <div className="text-sm text-gray-600">Orders Today</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-2xl font-bold text-green-600">{stats.revenue_today}</div>
              <div className="text-sm text-gray-600">Revenue Today</div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="container mx-auto px-4">
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setActiveTab('products')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'products'
                ? 'bg-green-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <ShoppingCart className="inline mr-2" />
            Products
          </button>
          <button
            onClick={() => setActiveTab('comparison')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'comparison'
                ? 'bg-green-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <TrendingUp className="inline mr-2" />
            Price Comparison
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 pb-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-2xl text-gray-600">Loading...</div>
          </div>
        ) : (
          <>
            {/* Products Grid */}
            {activeTab === 'products' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => (
                  <div key={product.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-shadow">
                    <div className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="text-xl font-bold text-gray-800">{product.name}</h3>
                        {product.organic_certified && (
                          <Eco className="text-green-600" />
                        )}
                      </div>
                      <p className="text-gray-600 mb-4">{product.description}</p>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Price:</span>
                          <span className="font-bold text-green-600">₹{product.price}/{product.unit}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Farmer:</span>
                          <span className="font-semibold">{product.farmer_name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Location:</span>
                          <span>{product.location}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Category:</span>
                          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">{product.category}</span>
                        </div>
                      </div>
                      <button className="w-full mt-4 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors">
                        Add to Cart
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Price Comparison */}
            {activeTab === 'comparison' && (
              <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                <div className="p-6">
                  <h2 className="text-2xl font-bold mb-6 text-gray-800">Real-Time Price Comparison</h2>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b-2 border-gray-200">
                          <th className="text-left py-3 px-4">Product</th>
                          <th className="text-center py-3 px-4">
                            <div className="flex flex-col items-center">
                              <Agriculture className="text-green-600 mb-1" />
                              <span>FarmConnect</span>
                            </div>
                          </th>
                          <th className="text-center py-3 px-4">
                            <div className="flex flex-col items-center">
                              <Store className="text-orange-600 mb-1" />
                              <span>BigBasket</span>
                            </div>
                          </th>
                          <th className="text-center py-3 px-4">
                            <div className="flex flex-col items-center">
                              <LocalShipping className="text-blue-600 mb-1" />
                              <span>Zepto</span>
                            </div>
                          </th>
                          <th className="text-center py-3 px-4">
                            <div className="flex flex-col items-center">
                              <Store className="text-purple-600 mb-1" />
                              <span>Swiggy</span>
                            </div>
                          </th>
                          <th className="text-center py-3 px-4 bg-green-50">Your Savings</th>
                        </tr>
                      </thead>
                      <tbody>
                        {priceComparison.map((item, index) => (
                          <tr key={index} className="border-b hover:bg-gray-50">
                            <td className="py-4 px-4 font-semibold">{item.product_name}</td>
                            <td className="text-center py-4 px-4">
                              <span className="text-green-600 font-bold text-lg">₹{item.farmer_price}</span>
                            </td>
                            <td className="text-center py-4 px-4">
                              <span className="text-gray-500 line-through">₹{item.bigbasket_price}</span>
                            </td>
                            <td className="text-center py-4 px-4">
                              <span className="text-gray-500 line-through">₹{item.zepto_price}</span>
                            </td>
                            <td className="text-center py-4 px-4">
                              <span className="text-gray-500 line-through">₹{item.swiggy_price}</span>
                            </td>
                            <td className="text-center py-4 px-4 bg-green-50">
                              <span className="bg-green-600 text-white px-3 py-1 rounded-full font-bold">
                                {item.savings_percentage}% OFF
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="mt-6 p-4 bg-green-100 rounded-lg">
                    <p className="text-center text-green-800 font-semibold">
                      Average Savings: 30-40% compared to retail platforms
                    </p>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="mb-2">FarmConnect - Empowering Farmers, Serving Consumers</p>
          <p className="text-sm text-gray-400">Made with ❤️ for Indian Agriculture</p>
        </div>
      </footer>
    </div>
  );
};

export default App;
