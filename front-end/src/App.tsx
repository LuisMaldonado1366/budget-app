import { useState } from 'react';
import { Plus, Trash2, FileText, Download, Edit2, Clock } from 'lucide-react';

interface Item {
  specifications: string;
  unit: string;
  quantity: number;
  unit_price: number;
}

interface Budget {
  company: string;
  address: string;
  attention: string;
  work_address: string;
  items: Item[];
  advance: number;
  acceptance_text: string;
}

interface BudgetResponse {
  id: number;
  company: string;
  address: string;
  attention: string;
  work_address: string;
  advance: number;
  subtotal: number;
  tax: number;
  total: number;
  pdf_filename: string;
  created_at: string;
  items?: BudgetItemDB[];
}

interface BudgetItemDB {
  id: number;
  budget_id: number;
  item_number: number;
  specifications: string;
  unit: string;
  quantity: number;
  unit_price: number;
  amount: number;
}

const API_URL = 'http://localhost:8800/budget';

export default function BudgetForm() {
  const [loading, setLoading] = useState(false);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [savedBudgets, setSavedBudgets] = useState<BudgetResponse[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [currentItem, setCurrentItem] = useState<Item>({
    specifications: '',
    unit: 'm²',
    quantity: 0,
    unit_price: 0
  });
  const [editingItem, setEditingItem] = useState<Item>({
    specifications: '',
    unit: 'm²',
    quantity: 0,
    unit_price: 0
  });
  const [budget, setBudget] = useState<Budget>({
    company: '',
    address: '',
    attention: '',
    work_address: '',
    items: [],
    advance: 0,
    acceptance_text: 'Acepto(amos) y autorizo(amos) para su realización'
  });

  const loadBudgets = async () => {
    try {
      const response = await fetch(API_URL);
      if (response.ok) {
        const data = await response.json();
        setSavedBudgets(data);
        setShowHistory(true);
      } else {
        console.error('Error al cargar presupuestos:', response.status);
        alert('Error al cargar el historial de presupuestos');
      }
    } catch (error) {
      console.error('Error al cargar presupuestos:', error);
      alert('Error de conexión al cargar el historial');
    }
  };

  const loadBudgetDetails = async (budgetId: number) => {
    try {
      const response = await fetch(`${API_URL}/${budgetId}`);
      if (response.ok) {
        const budgetData: BudgetResponse = await response.json();
        
        console.log('Datos recibidos:', budgetData);
        
        const loadedItems: Item[] = budgetData.items?.map(item => ({
          specifications: item.specifications,
          unit: item.unit,
          quantity: Number(item.quantity),
          unit_price: Number(item.unit_price)
        })) || [];
        
        console.log('Partidas cargadas:', loadedItems);
        
        setBudget({
          company: budgetData.company || '',
          address: budgetData.address || '',
          attention: budgetData.attention || '',
          work_address: budgetData.work_address || '',
          items: loadedItems,
          advance: Number(budgetData.advance) || 0,
          acceptance_text: 'Acepto(amos) y autorizo(amos) para su realización'
        });
        
        setShowHistory(false);
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        alert(`Presupuesto #${budgetId} cargado con ${loadedItems.length} partidas para edición`);
      } else {
        alert('Error al cargar el presupuesto');
      }
    } catch (error) {
      console.error('Error al cargar detalles del presupuesto:', error);
      alert('Error al cargar el presupuesto');
    }
  };

  const addOrUpdateItem = () => {
    if (!currentItem.specifications || currentItem.quantity <= 0 || currentItem.unit_price <= 0) {
      alert('Por favor completa todos los campos de la partida');
      return;
    }

    setBudget({
      ...budget,
      items: [...budget.items, currentItem]
    });

    setCurrentItem({
      specifications: '',
      unit: 'm²',
      quantity: 0,
      unit_price: 0
    });
  };

  const updateEditingItem = () => {
    if (!editingItem.specifications || editingItem.quantity <= 0 || editingItem.unit_price <= 0) {
      alert('Por favor completa todos los campos de la partida');
      return;
    }

    if (editingIndex !== null) {
      const newItems = [...budget.items];
      newItems[editingIndex] = editingItem;
      setBudget({ ...budget, items: newItems });
    }

    setShowEditModal(false);
    setEditingIndex(null);
    setEditingItem({
      specifications: '',
      unit: 'm²',
      quantity: 0,
      unit_price: 0
    });
  };

  const editItem = (index: number) => {
    setEditingItem(budget.items[index]);
    setEditingIndex(index);
    setShowEditModal(true);
  };

  const removeItem = (index: number) => {
    setBudget({
      ...budget,
      items: budget.items.filter((_, i) => i !== index)
    });
  };

  const cancelEdit = () => {
    setShowEditModal(false);
    setEditingIndex(null);
    setEditingItem({
      specifications: '',
      unit: 'm²',
      quantity: 0,
      unit_price: 0
    });
  };

  const calculateSubtotal = () => {
    return budget.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
  };

  const calculateTotal = () => {
    const subtotal = calculateSubtotal();
    const tax = subtotal * 0.16;
    return subtotal + tax;
  };

  const downloadBudget = async (budgetId: number, filename: string) => {
    try {
      const response = await fetch(`${API_URL}/${budgetId}/pdf`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Error al descargar el presupuesto');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error al descargar el presupuesto');
    }
  };

  const handleSubmit = async () => {
    if (budget.items.length === 0) {
      alert('Debes agregar al menos una partida');
      return;
    }

    setLoading(true);

    try {
      const budgetData = {
        company: budget.company.trim() || null,
        address: budget.address.trim() || null,
        attention: budget.attention.trim() || null,
        work_address: budget.work_address.trim() || null,
        items: budget.items,
        advance: budget.advance || 0,
        acceptance_text: budget.acceptance_text || 'Acepto(amos) y autorizo(amos) para su realización'
      };

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(budgetData),
      });

      if (response.ok) {
        const budgetResponse: BudgetResponse = await response.json();
        
        await downloadBudget(budgetResponse.id, budgetResponse.pdf_filename);
        
        alert(`Presupuesto #${budgetResponse.id} generado exitosamente`);
        
        setBudget({
          company: '',
          address: '',
          attention: '',
          work_address: '',
          items: [],
          advance: 0,
          acceptance_text: 'Acepto(amos) y autorizo(amos) para su realización'
        });
        
        await loadBudgets();
      } else {
        alert('Error al generar el presupuesto');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error al conectar con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <FileText className="w-8 h-8 text-indigo-600" />
              <h1 className="text-3xl font-bold text-gray-800">Generador de Presupuestos</h1>
            </div>
            <button
              onClick={() => {
                if (!showHistory) {
                  loadBudgets();
                } else {
                  setShowHistory(false);
                }
              }}
              className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <Clock className="w-5 h-5" />
              Ver Historial
            </button>
          </div>

          {/* Modal de Edición */}
          {showEditModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-800">Editar Partida #{(editingIndex ?? 0) + 1}</h2>
                  <button
                    onClick={cancelEdit}
                    className="text-gray-500 hover:text-gray-700 text-2xl"
                  >
                    ×
                  </button>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                    <div className="md:col-span-12">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Especificaciones *
                      </label>
                      <textarea
                        value={editingItem.specifications}
                        onChange={(e) => setEditingItem({ ...editingItem, specifications: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                        rows={4}
                        placeholder="Descripción detallada del trabajo"
                      />
                    </div>

                    <div className="md:col-span-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Unidad *
                      </label>
                      <select
                        value={editingItem.unit}
                        onChange={(e) => setEditingItem({ ...editingItem, unit: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      >
                        <option value="m²">m²</option>
                        <option value="m³">m³</option>
                        <option value="ml">ml</option>
                        <option value="pieza">pieza</option>
                        <option value="lote">lote</option>
                        <option value="salida">salida</option>
                        <option value="kg">kg</option>
                        <option value="lt">lt</option>
                      </select>
                    </div>

                    <div className="md:col-span-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Cantidad *
                      </label>
                      <input
                        type="number"
                        min="0.01"
                        step="0.01"
                        value={editingItem.quantity || ''}
                        onChange={(e) => setEditingItem({ ...editingItem, quantity: parseFloat(e.target.value) || 0 })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        placeholder="1"
                      />
                    </div>

                    <div className="md:col-span-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        P.U. *
                      </label>
                      <input
                        type="number"
                        min="0.01"
                        step="0.01"
                        value={editingItem.unit_price || ''}
                        onChange={(e) => setEditingItem({ ...editingItem, unit_price: parseFloat(e.target.value) || 0 })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        placeholder="0.00"
                      />
                    </div>
                  </div>

                  <div className="bg-indigo-50 p-4 rounded-lg">
                    <span className="text-sm text-gray-600">Importe: </span>
                    <span className="font-semibold text-gray-800 text-xl">
                      ${(editingItem.quantity * editingItem.unit_price).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                  </div>

                  <div className="flex justify-end gap-3 pt-4">
                    <button
                      type="button"
                      onClick={cancelEdit}
                      className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                    >
                      Cancelar
                    </button>
                    <button
                      type="button"
                      onClick={updateEditingItem}
                      className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                      Actualizar Partida
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Modal de Historial */}
          {showHistory && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-800">Historial de Presupuestos</h2>
                  <button
                    onClick={() => setShowHistory(false)}
                    className="text-gray-500 hover:text-gray-700 text-2xl"
                  >
                    ×
                  </button>
                </div>

                {savedBudgets.length === 0 ? (
                  <p className="text-gray-600 text-center py-8">No hay presupuestos guardados</p>
                ) : (
                  <div className="space-y-3">
                    {savedBudgets.map((saved) => {
                      // Construir el título dinámicamente
                      const parts = ['#' + saved.id];
                      const company = saved.company?.trim();
                      const attention = saved.attention?.trim();
                      
                      if (company) parts.push(company);
                      if (attention) parts.push(attention);
                      
                      const title = parts.join(' - ');
                      
                      return (
                        <div key={saved.id} className="bg-gray-50 p-4 rounded-lg border border-gray-200 hover:border-indigo-300 transition-colors">
                          <div className="flex justify-between items-start gap-4">
                            <div className="flex-1">
                              <div className="font-semibold text-gray-800 text-lg mb-1">
                                {title}
                              </div>
                              <div className="text-sm text-gray-600 mb-1">
                                📅 {new Date(saved.created_at).toLocaleString('es-MX')}
                              </div>
                              {saved.work_address?.trim() && (
                                <div className="text-sm text-gray-600 mb-1">
                                  📍 {saved.work_address.trim()}
                                </div>
                              )}
                              <div className="text-lg text-indigo-600 font-bold mt-2">
                                Total: ${saved.total ? saved.total.toLocaleString('es-MX', { minimumFractionDigits: 2 }) : '0.00'}
                              </div>
                            </div>
                            <div className="flex flex-col gap-2">
                              <button
                                onClick={() => loadBudgetDetails(saved.id)}
                                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors whitespace-nowrap"
                              >
                                <Edit2 className="w-4 h-4" />
                                Editar
                              </button>
                              <button
                                onClick={() => downloadBudget(saved.id, saved.pdf_filename)}
                                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors whitespace-nowrap"
                              >
                                <Download className="w-4 h-4" />
                                Descargar
                              </button>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="space-y-8">
            {/* Información General */}
            <section className="space-y-6">
              <h2 className="text-xl font-semibold text-gray-700 border-b pb-2">Información General</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Empresa
                  </label>
                  <input
                    type="text"
                    value={budget.company}
                    onChange={(e) => setBudget({ ...budget, company: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Nombre de la empresa"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Atención
                  </label>
                  <input
                    type="text"
                    value={budget.attention}
                    onChange={(e) => setBudget({ ...budget, attention: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Nombre del contacto"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Dirección de la Empresa
                  </label>
                  <input
                    type="text"
                    value={budget.address}
                    onChange={(e) => setBudget({ ...budget, address: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Calle, número, colonia, ciudad"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Dirección de la Obra
                  </label>
                  <input
                    type="text"
                    value={budget.work_address}
                    onChange={(e) => setBudget({ ...budget, work_address: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Ubicación donde se realizará el trabajo"
                  />
                </div>
              </div>
            </section>

            {/* Formulario de Partida */}
            <section className="space-y-6">
              <h2 className="text-xl font-semibold text-gray-700 border-b pb-2">
                Nueva Partida
              </h2>
              
              <div className="bg-indigo-50 p-6 rounded-lg space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                  <div className="md:col-span-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Especificaciones *
                    </label>
                    <textarea
                      value={currentItem.specifications}
                      onChange={(e) => setCurrentItem({ ...currentItem, specifications: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                      rows={3}
                      placeholder="Descripción detallada del trabajo"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Unidad *
                    </label>
                    <select
                      value={currentItem.unit}
                      onChange={(e) => setCurrentItem({ ...currentItem, unit: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      <option value="m²">m²</option>
                      <option value="m³">m³</option>
                      <option value="ml">ml</option>
                      <option value="pieza">pieza</option>
                      <option value="lote">lote</option>
                      <option value="salida">salida</option>
                      <option value="kg">kg</option>
                      <option value="lt">lt</option>
                    </select>
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cantidad *
                    </label>
                    <input
                      type="number"
                      min="0.01"
                      step="0.01"
                      value={currentItem.quantity || ''}
                      onChange={(e) => setCurrentItem({ ...currentItem, quantity: parseFloat(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="1"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      P.U. *
                    </label>
                    <input
                      type="number"
                      min="0.01"
                      step="0.01"
                      value={currentItem.unit_price || ''}
                      onChange={(e) => setCurrentItem({ ...currentItem, unit_price: parseFloat(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="0.00"
                    />
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <div>
                    <span className="text-sm text-gray-600">Importe: </span>
                    <span className="font-semibold text-gray-800 text-lg">
                      ${(currentItem.quantity * currentItem.unit_price).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={addOrUpdateItem}
                    className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    Agregar Partida
                  </button>
                </div>
              </div>
            </section>

            {/* Lista de Partidas */}
            {budget.items.length > 0 && (
              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-gray-700 border-b pb-2">
                  Partidas Agregadas ({budget.items.length})
                </h2>
                
                <div className="space-y-3">
                  {budget.items.map((item, index) => (
                    <div key={index} className="bg-gray-50 p-4 rounded-lg border border-gray-200 hover:border-indigo-300 transition-colors">
                      <div className="flex justify-between items-start gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-bold text-indigo-600">#{index + 1}</span>
                            <span className="text-sm text-gray-600">|</span>
                            <span className="text-sm font-medium text-gray-700">{item.unit}</span>
                            <span className="text-sm text-gray-600">|</span>
                            <span className="text-sm text-gray-700">Cantidad: {item.quantity}</span>
                          </div>
                          <p className="text-gray-800 mb-2">{item.specifications}</p>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">
                              P.U: ${item.unit_price.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                            </span>
                            <span className="font-semibold text-indigo-600">
                              Importe: ${(item.quantity * item.unit_price).toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                            </span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() => editItem(index)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Editar"
                          >
                            <Edit2 className="w-5 h-5" />
                          </button>
                          <button
                            type="button"
                            onClick={() => removeItem(index)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Eliminar"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Resumen */}
            <section className="bg-indigo-50 p-6 rounded-lg space-y-4">
              <h2 className="text-xl font-semibold text-gray-700">Resumen</h2>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-700">Subtotal:</span>
                  <span className="font-semibold">
                    ${calculateSubtotal().toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700">IVA (16%):</span>
                  <span className="font-semibold">
                    ${(calculateSubtotal() * 0.16).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="flex justify-between text-lg border-t pt-2">
                  <span className="font-bold text-gray-800">Total:</span>
                  <span className="font-bold text-indigo-600">
                    ${calculateTotal().toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>
              </div>

              <div className="mt-6">
                <div className="max-w-md">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Anticipo (%)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="1"
                    value={budget.advance || ''}
                    onChange={(e) => setBudget({ ...budget, advance: parseInt(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="50"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    Porcentaje del anticipo (0-100)
                  </p>
                </div>
              </div>
            </section>

            {/* Botón de envío */}
            <div className="flex justify-end">
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="flex items-center gap-2 px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed text-lg font-semibold"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Generando...
                  </>
                ) : (
                  <>
                    <Download className="w-5 h-5" />
                    Generar Presupuesto PDF
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}