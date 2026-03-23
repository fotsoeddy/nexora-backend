import React, { useState } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, FontWeight, Spacing, BorderRadius, Shadows } from '../../src/constants/theme';

type AppStatus = 'pending' | 'reviewing' | 'interview' | 'offered' | 'rejected';

const STATUS_CONFIG: Record<AppStatus, { label: string; color: string; bg: string; icon: string }> = {
  pending: { label: 'Pending', color: Colors.warning, bg: Colors.warningLight, icon: 'time' },
  reviewing: { label: 'Reviewing', color: Colors.info, bg: Colors.infoLight, icon: 'eye' },
  interview: { label: 'Interview', color: Colors.accent, bg: Colors.accent + '15', icon: 'chatbubbles' },
  offered: { label: 'Offered', color: Colors.success, bg: Colors.successLight, icon: 'checkmark-circle' },
  rejected: { label: 'Rejected', color: Colors.error, bg: Colors.errorLight, icon: 'close-circle' },
};

const APPLICATIONS = [
  { id: '1', title: 'Lead AI Solutions Architect', company: 'NeuralStream AI', location: 'Palo Alto', applied: '2 days ago', status: 'interview' as AppStatus, atsScore: 92, iconBg: '#3B82F6' },
  { id: '2', title: 'Senior Full-Stack Developer', company: 'Stripe', location: 'Remote', applied: '5 days ago', status: 'reviewing' as AppStatus, atsScore: 85, iconBg: '#6366F1' },
  { id: '3', title: 'ML Engineer', company: 'Google', location: 'London', applied: '1 week ago', status: 'pending' as AppStatus, atsScore: 78, iconBg: '#10B981' },
  { id: '4', title: 'Data Engineer', company: 'Amazon', location: 'Seattle', applied: '2 weeks ago', status: 'offered' as AppStatus, atsScore: 90, iconBg: '#F59E0B' },
  { id: '5', title: 'Backend Developer', company: 'Meta', location: 'Paris', applied: '3 weeks ago', status: 'rejected' as AppStatus, atsScore: 65, iconBg: '#EF4444' },
];

const TABS = ['All', 'Pending', 'Reviewing', 'Interview', 'Offered'] as const;

export default function ApplicationsScreen() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<string>('All');

  const filtered = activeTab === 'All'
    ? APPLICATIONS
    : APPLICATIONS.filter((a) => a.status === activeTab.toLowerCase());

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
        </Pressable>
        <Text style={styles.headerTitle}>My Applications</Text>
        <Text style={styles.countBadge}>{APPLICATIONS.length}</Text>
      </View>

      {/* Stats summary */}
      <View style={styles.statsRow}>
        {(['pending', 'reviewing', 'interview', 'offered'] as AppStatus[]).map((s) => {
          const cfg = STATUS_CONFIG[s];
          const count = APPLICATIONS.filter((a) => a.status === s).length;
          return (
            <View key={s} style={styles.statCard}>
              <View style={[styles.statDot, { backgroundColor: cfg.color }]} />
              <Text style={styles.statCount}>{count}</Text>
              <Text style={styles.statLabel}>{cfg.label}</Text>
            </View>
          );
        })}
      </View>

      {/* Filter tabs */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.tabsRow}>
        {TABS.map((tab) => (
          <Pressable
            key={tab}
            style={[styles.tabChip, activeTab === tab && styles.tabChipActive]}
            onPress={() => setActiveTab(tab)}
          >
            <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>{tab}</Text>
          </Pressable>
        ))}
      </ScrollView>

      {/* Applications list */}
      {filtered.map((app) => {
        const cfg = STATUS_CONFIG[app.status];
        return (
          <View key={app.id} style={styles.appCard}>
            <View style={styles.appHeader}>
              <View style={[styles.appIcon, { backgroundColor: app.iconBg }]}>
                <Ionicons name="business" size={18} color={Colors.textWhite} />
              </View>
              <View style={styles.appInfo}>
                <Text style={styles.appTitle}>{app.title}</Text>
                <Text style={styles.appCompany}>{app.company} • {app.location}</Text>
              </View>
            </View>
            <View style={styles.appFooter}>
              <View style={[styles.statusBadge, { backgroundColor: cfg.bg }]}>
                <Ionicons name={cfg.icon as any} size={12} color={cfg.color} />
                <Text style={[styles.statusText, { color: cfg.color }]}>{cfg.label}</Text>
              </View>
              <View style={styles.atsScoreBadge}>
                <Text style={styles.atsScoreText}>ATS {app.atsScore}%</Text>
              </View>
              <Text style={styles.appliedText}>{app.applied}</Text>
            </View>
          </View>
        );
      })}

      {filtered.length === 0 && (
        <View style={styles.emptyState}>
          <Ionicons name="document-text-outline" size={48} color={Colors.textTertiary} />
          <Text style={styles.emptyText}>No applications with this status</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { paddingTop: 52, paddingHorizontal: Spacing.xxl, paddingBottom: 40 },

  header: { flexDirection: 'row', alignItems: 'center', marginBottom: Spacing.xxl, gap: Spacing.md },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { flex: 1, fontSize: FontSize.xxl, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  countBadge: {
    backgroundColor: Colors.primary, borderRadius: BorderRadius.full,
    width: 28, height: 28, justifyContent: 'center', alignItems: 'center', textAlign: 'center',
    fontSize: FontSize.sm, fontWeight: FontWeight.bold, color: Colors.textWhite, lineHeight: 28,
    overflow: 'hidden',
  },

  statsRow: { flexDirection: 'row', gap: Spacing.md, marginBottom: Spacing.xxl },
  statCard: {
    flex: 1, backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.md,
    padding: Spacing.md, alignItems: 'center', gap: 2,
  },
  statDot: { width: 8, height: 8, borderRadius: 4, marginBottom: 2 },
  statCount: { fontSize: FontSize.xl, fontWeight: FontWeight.extrabold, color: Colors.textPrimary },
  statLabel: { fontSize: FontSize.xs, color: Colors.textSecondary },

  tabsRow: { gap: Spacing.sm, marginBottom: Spacing.xxl },
  tabChip: {
    paddingHorizontal: Spacing.xl, paddingVertical: Spacing.sm + 2, borderWidth: 1,
    borderColor: Colors.border, borderRadius: BorderRadius.full,
  },
  tabChipActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  tabText: { fontSize: FontSize.sm, fontWeight: FontWeight.medium, color: Colors.textSecondary },
  tabTextActive: { color: Colors.textWhite, fontWeight: FontWeight.semibold },

  appCard: {
    backgroundColor: Colors.background, borderWidth: 1, borderColor: Colors.borderLight,
    borderRadius: BorderRadius.lg, padding: Spacing.lg, marginBottom: Spacing.md,
    gap: Spacing.md, ...Shadows.sm,
  },
  appHeader: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  appIcon: { width: 40, height: 40, borderRadius: BorderRadius.md, justifyContent: 'center', alignItems: 'center' },
  appInfo: { flex: 1, gap: 2 },
  appTitle: { fontSize: FontSize.lg, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  appCompany: { fontSize: FontSize.sm, color: Colors.textSecondary },

  appFooter: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  statusBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, borderRadius: 6, paddingHorizontal: Spacing.md, paddingVertical: 4 },
  statusText: { fontSize: FontSize.xs, fontWeight: FontWeight.semibold },
  atsScoreBadge: { backgroundColor: Colors.backgroundTertiary, borderRadius: 6, paddingHorizontal: Spacing.md, paddingVertical: 4 },
  atsScoreText: { fontSize: FontSize.xs, fontWeight: FontWeight.bold, color: Colors.primary },
  appliedText: { fontSize: FontSize.xs, color: Colors.textTertiary, marginLeft: 'auto' },

  emptyState: { alignItems: 'center', paddingVertical: Spacing.huge, gap: Spacing.md },
  emptyText: { fontSize: FontSize.md, color: Colors.textTertiary },
});
