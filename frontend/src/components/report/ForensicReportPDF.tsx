import React from 'react';
import { Page, Text, View, Document, StyleSheet, Font } from '@react-pdf/renderer';

// Register fonts
Font.register({
  family: 'Roboto',
  src: 'https://cdnjs.cloudflare.com/ajax/libs/ink/3.1.10/fonts/Roboto/roboto-light-webfont.ttf'
});

const styles = StyleSheet.create({
  page: {
    padding: 30,
    backgroundColor: '#ffffff',
    fontFamily: 'Roboto'
  },
  header: {
    marginBottom: 20,
    borderBottom: 1,
    borderBottomColor: '#cccccc',
    paddingBottom: 10
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5
  },
  subtitle: {
    fontSize: 12,
    color: '#666666',
    marginBottom: 5
  },
  section: {
    marginBottom: 15
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    backgroundColor: '#f0f0f0',
    padding: 5
  },
  label: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: 2
  },
  value: {
    fontSize: 10,
    color: '#555555',
    marginBottom: 8
  },
  table: {
    display: 'table',
    width: 'auto',
    marginVertical: 10
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#eeeeee',
    paddingVertical: 5
  },
  tableCell: {
    flex: 1,
    fontSize: 9
  },
  tableHeader: {
    backgroundColor: '#f0f0f0',
    fontWeight: 'bold'
  },
  footer: {
    position: 'absolute',
    bottom: 30,
    left: 30,
    right: 30,
    textAlign: 'center',
    fontSize: 8,
    color: '#999999',
    borderTopWidth: 1,
    borderTopColor: '#cccccc',
    paddingTop: 10
  },
  badge: {
    padding: 3,
    borderRadius: 3,
    marginRight: 5
  },
  hashChain: {
    fontFamily: 'Courier',
    fontSize: 8,
    color: '#0066cc'
  }
});

interface ForensicReportProps {
  caseData: any;
  events: any[];
  evidence: any[];
  integrity: any;
  generatedAt: Date;
}

export const ForensicReportPDF: React.FC<ForensicReportProps> = ({
  caseData,
  events,
  evidence,
  integrity,
  generatedAt
}) => (
  <Document>
    <Page size="A4" style={styles.page}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Laporan Forensik NEMESIS V8+</Text>
        <Text style={styles.subtitle}>Platform Audit & Inspeksi Forensik</Text>
        <Text style={styles.subtitle}>Dibuat: {generatedAt.toLocaleString('id-ID')}</Text>
      </View>

      {/* Case Information */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Informasi Kasus</Text>
        <Text style={styles.label}>ID Kasus:</Text>
        <Text style={styles.value}>{caseData?.id || '-'}</Text>
        <Text style={styles.label}>Judul:</Text>
        <Text style={styles.value}>{caseData?.title || '-'}</Text>
        <Text style={styles.label}>Status:</Text>
        <Text style={styles.value}>{caseData?.status || '-'}</Text>
        <Text style={styles.label}>Prioritas:</Text>
        <Text style={styles.value}>{caseData?.priority || '-'}</Text>
        <Text style={styles.label}>Dibuat Pada:</Text>
        <Text style={styles.value}>{caseData?.created_at ? new Date(caseData.created_at).toLocaleString('id-ID') : '-'}</Text>
      </View>

      {/* Integrity Summary */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Integritas Sistem</Text>
        <Text style={styles.label}>Skor Integritas:</Text>
        <Text style={styles.value}>{integrity?.score || 100}%</Text>
        <Text style={styles.label}>Total Event:</Text>
        <Text style={styles.value}>{events.length}</Text>
        <Text style={styles.label}>Hash Chain:</Text>
        <Text style={[styles.value, styles.hashChain]}>
          {integrity?.first_hash ? `${integrity.first_hash.substring(0, 32)}...` : '-'}
        </Text>
        <Text style={styles.label}>Verifikasi Rantai:</Text>
        <Text style={styles.value}>{integrity?.valid ? '✓ Valid' : '✗ Rusak'}</Text>
      </View>

      {/* Event Timeline */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Linimasa Event</Text>
        <View style={styles.table}>
          <View style={[styles.tableRow, styles.tableHeader]}>
            <Text style={[styles.tableCell, { flex: 0.5 }]}>Versi</Text>
            <Text style={[styles.tableCell, { flex: 1.5 }]}>Event Type</Text>
            <Text style={[styles.tableCell, { flex: 2 }]}>Timestamp</Text>
            <Text style={[styles.tableCell, { flex: 1 }]}>User</Text>
          </View>
          {events.slice(0, 20).map((event, idx) => (
            <View key={idx} style={styles.tableRow}>
              <Text style={[styles.tableCell, { flex: 0.5 }]}>{event.version}</Text>
              <Text style={[styles.tableCell, { flex: 1.5 }]}>{event.event_type}</Text>
              <Text style={[styles.tableCell, { flex: 2 }]}>
                {event.timestamp ? new Date(event.timestamp).toLocaleString('id-ID') : '-'}
              </Text>
              <Text style={[styles.tableCell, { flex: 1 }]}>{event.user_id?.substring(0, 8)}...</Text>
            </View>
          ))}
        </View>
        {events.length > 20 && (
          <Text style={{ fontSize: 9, color: '#999', marginTop: 5 }}>
            ... dan {events.length - 20} event lainnya
          </Text>
        )}
      </View>

      {/* Evidence */}
      {evidence.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Bukti Digital</Text>
          {evidence.map((item, idx) => (
            <View key={idx} style={{ marginBottom: 10 }}>
              <Text style={styles.label}>{item.filename}</Text>
              <Text style={styles.value}>Hash: {item.file_hash}</Text>
              <Text style={styles.value}>Ukuran: {item.file_size} bytes</Text>
              <Text style={styles.value}>Upload: {new Date(item.uploaded_at).toLocaleString('id-ID')}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Footer */}
      <View style={styles.footer}>
        <Text>Dokumen ini dihasilkan secara otomatis oleh NEMESIS V8+ Forensic System</Text>
        <Text>Hash chain terverifikasi secara kriptografis (SHA256)</Text>
      </View>
    </Page>
  </Document>
);
