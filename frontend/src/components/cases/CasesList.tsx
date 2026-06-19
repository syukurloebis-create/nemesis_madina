// src/components/cases/CasesList.tsx - tambahkan batch actions
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useCaseStore } from '../../stores/caseStore';
import { api } from '../../services/api';
import toast from 'react-hot-toast';
import Pagination from '../common/Pagination';
import { Download, Trash2, CheckSquare, Square, X } from 'lucide-react';

const CasesList: React.FC = () => {
  const { cases, fetchCases, loading, error } = useCaseStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newCase, setNewCase] = useState({ title: '', description: '' });
  const [creating, setCreating] = useState(false);
  
  // Filter states
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  
  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  
  // Batch actions states
  const [selectedCases, setSelectedCases] = useState<Set<string>>(new Set());
  const [showBatchModal, setShowBatchModal] = useState(false);
  const [batchAction, setBatchAction] = useState<'delete' | 'status' | 'assign'>('delete');
  const [batchStatus, setBatchStatus] = useState<string>('');
  const [batchAssignee, setBatchAssignee] = useState<string>('');
  const [users, setUsers] = useState<{ id: string; name: string }[]>([]);

  useEffect(() => {
    fetchCases();
    loadUsers();
  }, []);

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
    setSelectedCases(new Set());
  }, [statusFilter, priorityFilter, searchTerm]);

  const loadUsers = async () => {
    try {
      // Mock users - in production, call API
      setUsers([
        { id: 'investigator-1', name: 'John Doe' },
        { id: 'investigator-2', name: 'Jane Smith' },
        { id: 'investigator-3', name: 'Mike Johnson' },
      ]);
    } catch (error) {
      console.error('Error loading users:', error);
    }
  };

  // Filtered cases
  const filteredCases = cases.filter(caseItem => {
    const matchesStatus = !statusFilter || caseItem.status === statusFilter;
    const matchesPriority = !priorityFilter || caseItem.priority === priorityFilter;
    const matchesSearch = !searchTerm || 
      caseItem.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      caseItem.id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesPriority && matchesSearch;
  });

  // Pagination calculations
  const totalPages = Math.ceil(filteredCases.length / itemsPerPage);
  const paginatedCases = filteredCases.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Batch actions handlers
  const toggleSelectAll = () => {
    if (selectedCases.size === paginatedCases.length) {
      setSelectedCases(new Set());
    } else {
      setSelectedCases(new Set(paginatedCases.map(c => c.id)));
    }
  };

  const toggleSelectCase = (caseId: string) => {
    const newSelected = new Set(selectedCases);
    if (newSelected.has(caseId)) {
      newSelected.delete(caseId);
    } else {
      newSelected.add(caseId);
    }
    setSelectedCases(newSelected);
  };

  const handleBatchDelete = async () => {
    if (selectedCases.size === 0) {
      toast.error('Pilih kasus yang akan dihapus');
      return;
    }
    
    if (!confirm(`Hapus ${selectedCases.size} kasus yang dipilih?`)) return;
    
    let successCount = 0;
    let failCount = 0;
    
    for (const caseId of selectedCases) {
      try {
        await api.deleteCase(caseId);
        successCount++;
      } catch (error) {
        failCount++;
      }
    }
    
    if (successCount > 0) {
      toast.success(`${successCount} kasus berhasil dihapus`);
    }
    if (failCount > 0) {
      toast.error(`${failCount} kasus gagal dihapus`);
    }
    
    setSelectedCases(new Set());
    await fetchCases();
    setShowBatchModal(false);
  };

  const handleBatchStatus = async () => {
    if (selectedCases.size === 0) {
      toast.error('Pilih kasus yang akan diupdate');
      return;
    }
    
    let successCount = 0;
    let failCount = 0;
    
    for (const caseId of selectedCases) {
      try {
        await api.updateCase(caseId, { status: batchStatus });
        successCount++;
      } catch (error) {
        failCount++;
      }
    }
    
    if (successCount > 0) {
      toast.success(`${successCount} kasus berhasil diupdate status menjadi ${batchStatus}`);
    }
    if (failCount > 0) {
      toast.error(`${failCount} kasus gagal diupdate`);
    }
    
    setSelectedCases(new Set());
    await fetchCases();
    setShowBatchModal(false);
  };

  const handleBatchAssign = async () => {
    if (selectedCases.size === 0) {
      toast.error('Pilih kasus yang akan diassign');
      return;
    }
    
    let successCount = 0;
    let failCount = 0;
    
    for (const caseId of selectedCases) {
      try {
        await api.assignCase(caseId, batchAssignee);
        successCount++;
      } catch (error) {
        failCount++;
      }
    }
    
    if (successCount > 0) {
      toast.success(`${successCount} kasus berhasil diassign`);
    }
    if (failCount > 0) {
      toast.error(`${failCount} kasus gagal diassign`);
    }
    
    setSelectedCases(new Set());
    await fetchCases();
    setShowBatchModal(false);
  };

  const exportToCSV = () => {
    const headers = ['ID', 'Title', 'Description', 'Status', 'Priority', 'Created At', 'Updated At'];
    const rows = cases.map(c => [
      c.id,
      `"${c.title.replace(/"/g, '""')}"`,
      `"${(c.description || '').replace(/"/g, '""')}"`,
      c.status,
      c.priority,
      new Date(c.created_at).toLocaleString(),
      new Date(c.updated_at).toLocaleString()
    ]);
    
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cases_export_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Cases exported to CSV');
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await api.createCase(newCase);
      toast.success('Case created successfully');
      setShowCreateModal(false);
      setNewCase({ title: '', description: '' });
      await fetchCases();
    } catch (error: any) {
      toast.error(error.message || 'Failed to create case');
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading cases...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Cases</h1>
        <div className="flex gap-2">
          {selectedCases.size > 0 && (
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setBatchAction('status');
                  setShowBatchModal(true);
                }}
                className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 flex items-center gap-2"
              >
                Update Status ({selectedCases.size})
              </button>
              <button
                onClick={() => {
                  setBatchAction('assign');
                  setShowBatchModal(true);
                }}
                className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 flex items-center gap-2"
              >
                Assign ({selectedCases.size})
              </button>
              <button
                onClick={() => {
                  setBatchAction('delete');
                  setShowBatchModal(true);
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Delete ({selectedCases.size})
              </button>
            </div>
          )}
          <button
            onClick={exportToCSV}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            + New Case
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow mb-6 p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search by title or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status Filter</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Status</option>
              <option value="OPEN">Open</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="CLOSED">Closed</option>
              <option value="ARCHIVED">Archived</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority Filter</label>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Priority</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>
        <div className="mt-3 flex justify-between items-center">
          <div className="text-sm text-gray-500">
            Showing {paginatedCases.length} of {filteredCases.length} cases
            {selectedCases.size > 0 && ` | ${selectedCases.size} selected`}
          </div>
          {(statusFilter || priorityFilter || searchTerm) && (
            <button
              onClick={() => {
                setStatusFilter('');
                setPriorityFilter('');
                setSearchTerm('');
              }}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Clear all filters
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {/* Cases Table with Checkboxes */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left">
                  <button
                    onClick={toggleSelectAll}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    {selectedCases.size === paginatedCases.length && paginatedCases.length > 0 ? (
                      <CheckSquare className="w-4 h-4" />
                    ) : (
                      <Square className="w-4 h-4" />
                    )}
                  </button>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedCases.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    No cases found
                  </td>
                </tr>
              ) : (
                paginatedCases.map((caseItem) => (
                  <tr key={caseItem.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <button
                        onClick={() => toggleSelectCase(caseItem.id)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        {selectedCases.has(caseItem.id) ? (
                          <CheckSquare className="w-4 h-4 text-blue-600" />
                        ) : (
                          <Square className="w-4 h-4" />
                        )}
                      </button>
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{caseItem.title}</td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-md truncate">
                      {caseItem.description}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        caseItem.status === 'OPEN' ? 'bg-green-100 text-green-800' :
                        caseItem.status === 'IN_PROGRESS' ? 'bg-yellow-100 text-yellow-800' :
                        caseItem.status === 'CLOSED' ? 'bg-gray-100 text-gray-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {caseItem.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">{caseItem.priority}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(caseItem.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <Link to={`/investigation/${caseItem.id}`} className="text-blue-600 hover:text-blue-800">
                        View →
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        </div>
      )}

      {/* Batch Action Modal */}
      {showBatchModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">
                {batchAction === 'delete' && 'Delete Cases'}
                {batchAction === 'status' && 'Update Status'}
                {batchAction === 'assign' && 'Assign Cases'}
              </h2>
              <button onClick={() => setShowBatchModal(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600">
                {selectedCases.size} case(s) selected
              </p>
            </div>

            {batchAction === 'status' && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">New Status</label>
                <select
                  value={batchStatus}
                  onChange={(e) => setBatchStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                >
                  <option value="">Select Status</option>
                  <option value="OPEN">Open</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="CLOSED">Closed</option>
                </select>
              </div>
            )}

            {batchAction === 'assign' && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Assign To</label>
                <select
                  value={batchAssignee}
                  onChange={(e) => setBatchAssignee(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                >
                  <option value="">Select Investigator</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>{user.name}</option>
                  ))}
                </select>
              </div>
            )}

            {batchAction === 'delete' && (
              <div className="mb-4 p-3 bg-red-50 rounded-md">
                <p className="text-sm text-red-600">
                  Warning: This action cannot be undone. {selectedCases.size} case(s) will be permanently deleted.
                </p>
              </div>
            )}

            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowBatchModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={batchAction === 'delete' ? handleBatchDelete : batchAction === 'status' ? handleBatchStatus : handleBatchAssign}
                className={`px-4 py-2 rounded-md text-white ${
                  batchAction === 'delete' ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Case Modal (existing) */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Create New Case</h2>
              <button onClick={() => setShowCreateModal(false)} className="text-gray-400 hover:text-gray-600">×</button>
            </div>
            
            <form onSubmit={handleCreateCase}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  required
                  value={newCase.title}
                  onChange={(e) => setNewCase({ ...newCase, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newCase.description}
                  onChange={(e) => setNewCase({ ...newCase, description: e.target.value })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {creating ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CasesList;