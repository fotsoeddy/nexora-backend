import React, { useState } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, FontWeight, Spacing, BorderRadius, Shadows } from '../../src/constants/theme';

const ACTIVE_ALERTS = [
  { id: '1', keywords: 'AI Engineer', location: 'Remote', frequency: 'Daily', matches: 12, active: true },
  { id: '2', keywords: 'Data Scientist', location: 'Paris', frequency: 'Weekly', matches: 8, active: true },
  { id: '3', keywords: 'ML Ops', location: 'Worldwide', frequency: 'Instant', matches: 3, active: false },
];

export default function AlertsScreen() {
  const router = useRouter();
  const [alerts, setAlerts] = useState(ACTIVE_ALERTS);
  const [showCreate, setShowCreate] = useState(false);

  const toggleAlert = (id: string) => {
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, active: !a.active } : a)));
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
        </Pressable>
        <Text style={styles.headerTitle}>Job Alerts</Text>
        <Pressable style={styles.addBtn} onPress={() => setShowCreate(!showCreate)}>
          <Ionicons name={showCreate ? 'close' : 'add'} size={20} color={Colors.textWhite} />
        </Pressable>
      </View>

      {showCreate && (
        <View style={styles.createCard}>
          <Text style={styles.createTitle}>Create New Alert</Text>
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Keywords</Text>
            <View style={styles.inputContainer}>
              <Ionicons name="search" size={18} color={Colors.textTertiary} />
              <TextInput style={styles.input} placeholder="e.g. React Developer" placeholderTextColor={Colors.textTertiary} />
            </View>
          </View>
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Location</Text>
            <View style={styles.inputContainer}>
              <Ionicons name="location-outline" size={18} color={Colors.textTertiary} />
              <TextInput style={styles.input} placeholder="e.g. Remote, Paris" placeholderTextColor={Colors.textTertiary} />
            </View>
          </View>
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Frequency</Text>
            <View style={styles.freqRow}>
              {['Instant', 'Daily', 'Weekly'].map((f, i) => (
                <Pressable key={f} style={[styles.freqChip, i === 0 && styles.freqChipActive]}>
                  <Text style={[styles.freqText, i === 0 && styles.freqTextActive]}>{f}</Text>
                </Pressable>
              ))}
            </View>
          </View>
          <Pressable style={styles.primaryButton}>
            <Ionicons name="notifications" size={20} color={Colors.textWhite} />
            <Text style={styles.primaryButtonText}>Create Alert</Text>
          </Pressable>
        </View>
      )}

      <Text style={styles.sectionTitle}>Active Alerts ({alerts.filter((a) => a.active).length})</Text>

      {alerts.map((alert) => (
        <View key={alert.id} style={[styles.alertCard, !alert.active && styles.alertCardInactive]}>
          <View style={styles.alertHeader}>
            <View style={[styles.alertIcon, { backgroundColor: alert.active ? Colors.accent + '15' : Colors.backgroundTertiary }]}>
              <Ionicons name="notifications" size={18} color={alert.active ? Colors.accent : Colors.textTertiary} />
            </View>
            <View style={styles.alertInfo}>
              <Text style={styles.alertKeywords}>{alert.keywords}</Text>
              <View style={styles.alertMeta}>
                <Ionicons name="location" size={12} color={Colors.textTertiary} />
                <Text style={styles.alertMetaText}>{alert.location}</Text>
                <Text style={styles.alertDot}>•</Text>
                <Text style={styles.alertMetaText}>{alert.frequency}</Text>
              </View>
            </View>
            <Switch
              value={alert.active}
              onValueChange={() => toggleAlert(alert.id)}
              trackColor={{ false: Colors.border, true: Colors.accent + '50' }}
              thumbColor={alert.active ? Colors.accent : Colors.textTertiary}
            />
          </View>
          <View style={styles.alertFooter}>
            <View style={styles.matchesBadge}>
              <Ionicons name="briefcase" size={12} color={Colors.success} />
              <Text style={styles.matchesText}>{alert.matches} new matches</Text>
            </View>
            <Pressable>
              <Text style={styles.viewMatchesLink}>View →</Text>
            </Pressable>
          </View>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { paddingTop: 52, paddingHorizontal: Spacing.xxl, paddingBottom: 40 },

  header: { flexDirection: 'row', alignItems: 'center', marginBottom: Spacing.xxl, gap: Spacing.md },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { flex: 1, fontSize: FontSize.xxl, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  addBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: Colors.primary, justifyContent: 'center', alignItems: 'center' },

  createCard: {
    backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.lg,
    padding: Spacing.xl, marginBottom: Spacing.xxl, gap: Spacing.lg,
  },
  createTitle: { fontSize: FontSize.xl, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  inputGroup: { gap: Spacing.sm },
  label: { fontSize: FontSize.md, fontWeight: FontWeight.semibold, color: Colors.textPrimary },
  inputContainer: {
    flexDirection: 'row', alignItems: 'center', borderWidth: 1, borderColor: Colors.border,
    borderRadius: BorderRadius.md, paddingHorizontal: Spacing.lg, height: 48, gap: Spacing.md,
    backgroundColor: Colors.background,
  },
  input: { flex: 1, fontSize: FontSize.md, color: Colors.textPrimary },

  freqRow: { flexDirection: 'row', gap: Spacing.md },
  freqChip: { flex: 1, alignItems: 'center', paddingVertical: Spacing.md, borderWidth: 1, borderColor: Colors.border, borderRadius: BorderRadius.md },
  freqChipActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  freqText: { fontSize: FontSize.sm, fontWeight: FontWeight.medium, color: Colors.textSecondary },
  freqTextActive: { color: Colors.textWhite, fontWeight: FontWeight.semibold },

  sectionTitle: { fontSize: FontSize.lg, fontWeight: FontWeight.bold, color: Colors.textPrimary, marginBottom: Spacing.lg },

  alertCard: {
    backgroundColor: Colors.background, borderWidth: 1, borderColor: Colors.borderLight,
    borderRadius: BorderRadius.lg, padding: Spacing.lg, marginBottom: Spacing.md, ...Shadows.sm,
  },
  alertCardInactive: { opacity: 0.6 },
  alertHeader: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md, marginBottom: Spacing.md },
  alertIcon: { width: 40, height: 40, borderRadius: BorderRadius.md, justifyContent: 'center', alignItems: 'center' },
  alertInfo: { flex: 1, gap: 2 },
  alertKeywords: { fontSize: FontSize.lg, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  alertMeta: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  alertMetaText: { fontSize: FontSize.xs, color: Colors.textTertiary },
  alertDot: { color: Colors.textTertiary },
  alertFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  matchesBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: Colors.successLight,
    borderRadius: 6, paddingHorizontal: Spacing.md, paddingVertical: 4,
  },
  matchesText: { fontSize: FontSize.xs, fontWeight: FontWeight.semibold, color: Colors.success },
  viewMatchesLink: { fontSize: FontSize.md, fontWeight: FontWeight.semibold, color: Colors.accent },

  primaryButton: {
    backgroundColor: Colors.primary, borderRadius: BorderRadius.xl, paddingVertical: Spacing.lg,
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: Spacing.sm,
  },
  primaryButtonText: { color: Colors.textWhite, fontSize: FontSize.lg, fontWeight: FontWeight.semibold },
});
