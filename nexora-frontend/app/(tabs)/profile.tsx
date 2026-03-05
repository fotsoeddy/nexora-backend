import React from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, FontWeight, Spacing, BorderRadius } from '../../src/constants/theme';

const MENU_SECTIONS = [
  {
    title: 'Career Tools',
    items: [
      { icon: 'document-text-outline' as const, label: 'My CVs', route: '/cv/cover-letter', badge: '2' },
      { icon: 'folder-outline' as const, label: 'Applications', route: '/applications', badge: '12' },
      { icon: 'bookmark-outline' as const, label: 'Saved Jobs', route: '/saved', badge: '4' },
      { icon: 'notifications-outline' as const, label: 'Job Alerts', route: '/alerts', badge: '5' },
    ],
  },
  {
    title: 'AI Features',
    items: [
      { icon: 'sparkles-outline' as const, label: 'AI Assistant', route: '/chat' },
      { icon: 'analytics-outline' as const, label: 'Salary Estimator', route: '/salary' },
      { icon: 'chatbubbles-outline' as const, label: 'Mock Interview', route: '/interview/voice' },
      { icon: 'create-outline' as const, label: 'Cover Letter AI', route: '/cv/cover-letter' },
    ],
  },
  {
    title: 'Account',
    items: [
      { icon: 'card-outline' as const, label: 'Subscription', route: '' },
      { icon: 'settings-outline' as const, label: 'Settings', route: '' },
      { icon: 'help-circle-outline' as const, label: 'Help & Support', route: '' },
    ],
  },
];

export default function ProfileScreen() {
  const router = useRouter();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Profile</Text>
        <Pressable>
          <Ionicons name="create-outline" size={22} color={Colors.accent} />
        </Pressable>
      </View>

      {/* User card */}
      <View style={styles.userCard}>
        <View style={styles.avatarSection}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>EF</Text>
          </View>
          <View style={styles.planBadge}>
            <Ionicons name="star" size={10} color={Colors.textWhite} />
            <Text style={styles.planText}>PRO</Text>
          </View>
        </View>
        <View style={styles.userInfo}>
          <Text style={styles.userName}>Eddy Fotso</Text>
          <Text style={styles.userEmail}>eddy@nexora.ai</Text>
          <Text style={styles.userRole}>AI Solutions Engineer</Text>
        </View>
      </View>

      {/* Stats */}
      <View style={styles.statsRow}>
        <Pressable style={styles.statCard} onPress={() => router.push('/applications')}>
          <Text style={styles.statNumber}>12</Text>
          <Text style={styles.statLabel}>Applications</Text>
          <View style={styles.statTrend}>
            <Ionicons name="trending-up" size={12} color={Colors.success} />
            <Text style={styles.statTrendText}>+3</Text>
          </View>
        </Pressable>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>85</Text>
          <Text style={styles.statLabel}>ATS Score</Text>
          <View style={styles.statTrend}>
            <Ionicons name="trending-up" size={12} color={Colors.success} />
            <Text style={styles.statTrendText}>+5</Text>
          </View>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>3</Text>
          <Text style={styles.statLabel}>Interviews</Text>
          <View style={styles.statTrend}>
            <Ionicons name="trending-up" size={12} color={Colors.success} />
            <Text style={styles.statTrendText}>+1</Text>
          </View>
        </View>
      </View>

      {/* Menu sections */}
      {MENU_SECTIONS.map((section, sIdx) => (
        <View key={sIdx} style={styles.menuSection}>
          <Text style={styles.menuSectionTitle}>{section.title}</Text>
          <View style={styles.menuContainer}>
            {section.items.map((item, idx) => (
              <Pressable
                key={idx}
                style={[styles.menuItem, idx === section.items.length - 1 && styles.menuItemLast]}
                onPress={() => item.route ? router.push(item.route as any) : null}
              >
                <View style={styles.menuIconContainer}>
                  <Ionicons name={item.icon} size={20} color={Colors.textPrimary} />
                </View>
                <Text style={styles.menuLabel}>{item.label}</Text>
                {(item as any).badge && (
                  <View style={styles.menuBadge}>
                    <Text style={styles.menuBadgeText}>{(item as any).badge}</Text>
                  </View>
                )}
                <Ionicons name="chevron-forward" size={16} color={Colors.textTertiary} />
              </Pressable>
            ))}
          </View>
        </View>
      ))}

      {/* Logout */}
      <Pressable style={styles.logoutButton} onPress={() => router.replace('/(auth)/signin')}>
        <Ionicons name="log-out-outline" size={22} color={Colors.error} />
        <Text style={styles.logoutText}>Log Out</Text>
      </Pressable>

      {/* Version */}
      <Text style={styles.version}>Nexora AI v1.0.0</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { paddingTop: 56, paddingHorizontal: Spacing.xxl, paddingBottom: 32 },

  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    marginBottom: Spacing.xxl,
  },
  headerTitle: { fontSize: FontSize.xxl, fontWeight: FontWeight.bold, color: Colors.textPrimary },

  userCard: {
    flexDirection: 'row', alignItems: 'center', gap: Spacing.xl,
    marginBottom: Spacing.xxl,
  },
  avatarSection: { position: 'relative' },
  avatar: {
    width: 64, height: 64, borderRadius: 32, backgroundColor: Colors.primary,
    justifyContent: 'center', alignItems: 'center',
  },
  avatarText: { fontSize: FontSize.xxl, fontWeight: FontWeight.bold, color: Colors.textWhite },
  planBadge: {
    position: 'absolute', bottom: -2, right: -2, flexDirection: 'row', alignItems: 'center', gap: 2,
    backgroundColor: Colors.accent, borderRadius: BorderRadius.full, paddingHorizontal: 6,
    paddingVertical: 2, borderWidth: 2, borderColor: Colors.background,
  },
  planText: { fontSize: 9, fontWeight: FontWeight.extrabold, color: Colors.textWhite },
  userInfo: { flex: 1, gap: 2 },
  userName: { fontSize: FontSize.xxl, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  userEmail: { fontSize: FontSize.sm, color: Colors.textSecondary },
  userRole: { fontSize: FontSize.sm, color: Colors.accent, fontWeight: FontWeight.medium, marginTop: 2 },

  statsRow: { flexDirection: 'row', gap: Spacing.md, marginBottom: Spacing.xxl },
  statCard: {
    flex: 1, backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.lg,
    padding: Spacing.lg, alignItems: 'center', gap: 4,
  },
  statNumber: { fontSize: FontSize.xxxl, fontWeight: FontWeight.extrabold, color: Colors.primary },
  statLabel: { fontSize: FontSize.xs, color: Colors.textSecondary, fontWeight: FontWeight.medium },
  statTrend: { flexDirection: 'row', alignItems: 'center', gap: 2 },
  statTrendText: { fontSize: FontSize.xs, color: Colors.success, fontWeight: FontWeight.bold },

  menuSection: { marginBottom: Spacing.xxl },
  menuSectionTitle: {
    fontSize: FontSize.sm, fontWeight: FontWeight.bold, color: Colors.textSecondary,
    letterSpacing: 0.5, marginBottom: Spacing.md, textTransform: 'uppercase',
  },
  menuContainer: {
    backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.lg, overflow: 'hidden',
  },
  menuItem: {
    flexDirection: 'row', alignItems: 'center', padding: Spacing.lg,
    gap: Spacing.lg, borderBottomWidth: 1, borderBottomColor: Colors.borderLight,
  },
  menuItemLast: { borderBottomWidth: 0 },
  menuIconContainer: {
    width: 36, height: 36, borderRadius: BorderRadius.sm, backgroundColor: Colors.background,
    justifyContent: 'center', alignItems: 'center',
  },
  menuLabel: { flex: 1, fontSize: FontSize.lg, fontWeight: FontWeight.medium, color: Colors.textPrimary },
  menuBadge: {
    backgroundColor: Colors.primary, borderRadius: BorderRadius.full,
    paddingHorizontal: 8, paddingVertical: 2, marginRight: Spacing.sm,
  },
  menuBadgeText: { fontSize: FontSize.xs, fontWeight: FontWeight.bold, color: Colors.textWhite },

  logoutButton: {
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: Spacing.md,
    borderWidth: 1, borderColor: Colors.error + '40', borderRadius: BorderRadius.xl,
    paddingVertical: Spacing.lg, marginBottom: Spacing.lg,
  },
  logoutText: { fontSize: FontSize.lg, fontWeight: FontWeight.semibold, color: Colors.error },

  version: { textAlign: 'center', fontSize: FontSize.xs, color: Colors.textTertiary },
});
