import React from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, FontWeight, Spacing, BorderRadius, Shadows } from '../../src/constants/theme';

const RECOMMENDED_JOBS = [
  {
    id: '1',
    title: 'Senior UI Designer',
    company: 'Stripe',
    location: 'San Francisco',
    salary: '$140k - $190k',
    isNew: true,
    icon: 'color-palette' as const,
    iconBg: '#6366F1',
  },
  {
    id: '2',
    title: 'Product Manager',
    company: 'Airbnb',
    location: 'New York',
    salary: '$160k - $210k',
    isNew: false,
    icon: 'cube' as const,
    iconBg: '#EC4899',
  },
  {
    id: '3',
    title: 'Data Analyst',
    company: 'Google',
    location: 'London',
    salary: '$120k - $160k',
    isNew: true,
    icon: 'stats-chart' as const,
    iconBg: '#10B981',
  },
];

const AI_FEATURES = [
  { icon: 'document-text', label: 'CV Analysis', subtitle: 'ATS Score', route: '/(tabs)/interview', color: Colors.accent, bg: Colors.accent + '12' },
  { icon: 'chatbubbles', label: 'AI Interview', subtitle: 'Practice', route: '/interview/voice', color: Colors.primaryLight, bg: Colors.primaryLight + '12' },
  { icon: 'sparkles', label: 'AI Chat', subtitle: 'Assistant', route: '/chat', color: Colors.success, bg: Colors.success + '12' },
  { icon: 'create', label: 'Cover Letter', subtitle: 'Generate', route: '/cv/cover-letter', color: '#8B5CF6', bg: '#8B5CF615' },
];

export default function HomeScreen() {
  const router = useRouter();

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Good morning 👋</Text>
          <Text style={styles.userName}>Welcome back, Eddy</Text>
        </View>
        <Pressable style={styles.notifButton}>
          <Ionicons name="notifications" size={22} color={Colors.primary} />
          <View style={styles.notifDot} />
        </Pressable>
      </View>

      {/* Search */}
      <Pressable style={styles.searchContainer}>
        <Ionicons name="search" size={20} color={Colors.textTertiary} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search jobs, roles, or skills..."
          placeholderTextColor={Colors.textTertiary}
        />
        <View style={styles.searchFilter}>
          <Ionicons name="options" size={18} color={Colors.accent} />
        </View>
      </Pressable>

      {/* Stats Bar */}
      <View style={styles.statsBar}>
        <Pressable style={styles.statItem} onPress={() => router.push('/applications')}>
          <Text style={styles.statNumber}>12</Text>
          <Text style={styles.statLabel}>Applied</Text>
        </Pressable>
        <View style={styles.statDivider} />
        <Pressable style={styles.statItem}>
          <Text style={styles.statNumber}>85</Text>
          <Text style={styles.statLabel}>ATS Score</Text>
        </Pressable>
        <View style={styles.statDivider} />
        <Pressable style={styles.statItem} onPress={() => router.push('/alerts')}>
          <Text style={styles.statNumber}>5</Text>
          <Text style={styles.statLabel}>Alerts</Text>
        </Pressable>
        <View style={styles.statDivider} />
        <Pressable style={styles.statItem} onPress={() => router.push('/saved')}>
          <Text style={styles.statNumber}>4</Text>
          <Text style={styles.statLabel}>Saved</Text>
        </Pressable>
      </View>

      {/* AI Workspace grid */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>AI Workspace</Text>
      </View>
      <View style={styles.aiGrid}>
        {AI_FEATURES.map((f, i) => (
          <Pressable
            key={i}
            style={[styles.aiCard, { backgroundColor: f.bg }]}
            onPress={() => router.push(f.route as any)}
          >
            <View style={[styles.aiCardIcon, { backgroundColor: f.color + '20' }]}>
              <Ionicons name={f.icon as any} size={22} color={f.color} />
            </View>
            <Text style={styles.aiCardTitle}>{f.label}</Text>
            <Text style={styles.aiCardSubtitle}>{f.subtitle}</Text>
          </Pressable>
        ))}
      </View>

      {/* Recommended Jobs */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Recommended Jobs</Text>
        <Pressable onPress={() => router.push('/(tabs)/jobs')}>
          <Text style={styles.seeAll}>See all</Text>
        </Pressable>
      </View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.jobsScrollContent}>
        {RECOMMENDED_JOBS.map((job) => (
          <Pressable
            key={job.id}
            style={styles.jobCard}
            onPress={() => router.push(`/job/${job.id}`)}
          >
            {job.isNew && (
              <View style={styles.newBadge}>
                <Text style={styles.newBadgeText}>NEW</Text>
              </View>
            )}
            <View style={[styles.jobIconContainer, { backgroundColor: job.iconBg }]}>
              <Ionicons name={job.icon} size={22} color={Colors.textWhite} />
            </View>
            <Text style={styles.jobTitle} numberOfLines={2}>{job.title}</Text>
            <Text style={styles.jobCompany}>{job.company} • {job.location}</Text>
            <Text style={styles.jobSalary}>{job.salary}</Text>
          </Pressable>
        ))}
      </ScrollView>

      {/* Quick Actions */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
      </View>
      <View style={styles.quickActions}>
        <Pressable style={styles.quickAction} onPress={() => router.push('/salary')}>
          <View style={[styles.quickActionIcon, { backgroundColor: Colors.success + '15' }]}>
            <Ionicons name="cash" size={22} color={Colors.success} />
          </View>
          <Text style={styles.quickActionText}>Salary{'\n'}Estimator</Text>
        </Pressable>
        <Pressable style={styles.quickAction} onPress={() => router.push('/chat')}>
          <View style={[styles.quickActionIcon, { backgroundColor: Colors.accent + '15' }]}>
            <Ionicons name="sparkles" size={22} color={Colors.accent} />
          </View>
          <Text style={styles.quickActionText}>AI{'\n'}Assistant</Text>
        </Pressable>
        <Pressable style={styles.quickAction} onPress={() => router.push('/alerts')}>
          <View style={[styles.quickActionIcon, { backgroundColor: Colors.warning + '15' }]}>
            <Ionicons name="notifications" size={22} color={Colors.warning} />
          </View>
          <Text style={styles.quickActionText}>Job{'\n'}Alerts</Text>
        </Pressable>
        <Pressable style={styles.quickAction} onPress={() => router.push('/applications')}>
          <View style={[styles.quickActionIcon, { backgroundColor: Colors.info + '15' }]}>
            <Ionicons name="folder" size={22} color={Colors.info} />
          </View>
          <Text style={styles.quickActionText}>My{'\n'}Applications</Text>
        </Pressable>
      </View>

      {/* AI Chat CTA */}
      <Pressable style={styles.chatCta} onPress={() => router.push('/chat')}>
        <View style={styles.chatCtaLeft}>
          <View style={styles.chatCtaAvatar}>
            <Ionicons name="sparkles" size={20} color={Colors.textWhite} />
          </View>
          <View>
            <Text style={styles.chatCtaTitle}>Need career advice?</Text>
            <Text style={styles.chatCtaSubtitle}>Chat with Nexora AI Assistant</Text>
          </View>
        </View>
        <Ionicons name="chevron-forward" size={20} color={Colors.textWhite} />
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { paddingTop: 56, paddingBottom: 24 },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: Spacing.xxl, marginBottom: Spacing.xl,
  },
  greeting: { fontSize: FontSize.md, color: Colors.textSecondary, marginBottom: 2 },
  userName: { fontSize: FontSize.xxl, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  notifButton: {
    width: 44, height: 44, borderRadius: BorderRadius.md, backgroundColor: Colors.backgroundSecondary,
    justifyContent: 'center', alignItems: 'center',
  },
  notifDot: {
    position: 'absolute', top: 10, right: 12, width: 8, height: 8,
    borderRadius: 4, backgroundColor: Colors.error,
  },
  searchContainer: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.backgroundSecondary,
    borderRadius: BorderRadius.md, paddingHorizontal: Spacing.lg, height: 48,
    marginHorizontal: Spacing.xxl, marginBottom: Spacing.xl, gap: Spacing.md,
  },
  searchInput: { flex: 1, fontSize: FontSize.md, color: Colors.textPrimary },
  searchFilter: {
    width: 32, height: 32, borderRadius: BorderRadius.sm,
    backgroundColor: Colors.accent + '12', justifyContent: 'center', alignItems: 'center',
  },

  statsBar: {
    flexDirection: 'row', marginHorizontal: Spacing.xxl, backgroundColor: Colors.backgroundSecondary,
    borderRadius: BorderRadius.lg, paddingVertical: Spacing.lg, marginBottom: Spacing.xxl,
  },
  statItem: { flex: 1, alignItems: 'center', gap: 2 },
  statNumber: { fontSize: FontSize.xl, fontWeight: FontWeight.extrabold, color: Colors.primary },
  statLabel: { fontSize: FontSize.xs, color: Colors.textSecondary },
  statDivider: { width: 1, backgroundColor: Colors.border },

  sectionHeader: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: Spacing.xxl, marginBottom: Spacing.lg, marginTop: Spacing.sm,
  },
  sectionTitle: { fontSize: FontSize.xl, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  seeAll: { fontSize: FontSize.md, color: Colors.accent, fontWeight: FontWeight.medium },

  aiGrid: {
    flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: Spacing.xxl,
    gap: Spacing.md, marginBottom: Spacing.xxl,
  },
  aiCard: {
    width: '47%', borderRadius: BorderRadius.lg, padding: Spacing.lg, gap: Spacing.sm,
  },
  aiCardIcon: {
    width: 40, height: 40, borderRadius: BorderRadius.md,
    justifyContent: 'center', alignItems: 'center',
  },
  aiCardTitle: { fontSize: FontSize.md, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  aiCardSubtitle: { fontSize: FontSize.sm, color: Colors.textSecondary },

  jobsScrollContent: { paddingHorizontal: Spacing.xxl, gap: Spacing.md, paddingBottom: Spacing.lg },
  jobCard: {
    width: 170, backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.lg,
    padding: Spacing.lg, gap: Spacing.sm,
  },
  newBadge: {
    position: 'absolute', top: Spacing.md, right: Spacing.md,
    backgroundColor: Colors.success + '20', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6,
  },
  newBadgeText: { fontSize: FontSize.xs, fontWeight: FontWeight.bold, color: Colors.success },
  jobIconContainer: {
    width: 40, height: 40, borderRadius: BorderRadius.sm,
    justifyContent: 'center', alignItems: 'center', marginBottom: Spacing.xs,
  },
  jobTitle: { fontSize: FontSize.md, fontWeight: FontWeight.bold, color: Colors.textPrimary, lineHeight: 20 },
  jobCompany: { fontSize: FontSize.xs, color: Colors.textSecondary },
  jobSalary: { fontSize: FontSize.md, fontWeight: FontWeight.semibold, color: Colors.primary, marginTop: Spacing.xs },

  quickActions: {
    flexDirection: 'row', paddingHorizontal: Spacing.xxl,
    gap: Spacing.md, marginBottom: Spacing.xxl,
  },
  quickAction: { flex: 1, alignItems: 'center', gap: Spacing.sm },
  quickActionIcon: {
    width: 52, height: 52, borderRadius: BorderRadius.lg,
    justifyContent: 'center', alignItems: 'center',
  },
  quickActionText: {
    fontSize: FontSize.xs, fontWeight: FontWeight.medium,
    color: Colors.textPrimary, textAlign: 'center', lineHeight: 16,
  },

  chatCta: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    backgroundColor: Colors.primary, borderRadius: BorderRadius.lg,
    paddingVertical: Spacing.lg, paddingHorizontal: Spacing.xl,
    marginHorizontal: Spacing.xxl,
  },
  chatCtaLeft: { flexDirection: 'row', alignItems: 'center', gap: Spacing.lg },
  chatCtaAvatar: {
    width: 40, height: 40, borderRadius: 20, backgroundColor: Colors.accent,
    justifyContent: 'center', alignItems: 'center',
  },
  chatCtaTitle: { fontSize: FontSize.md, fontWeight: FontWeight.bold, color: Colors.textWhite },
  chatCtaSubtitle: { fontSize: FontSize.xs, color: 'rgba(255,255,255,0.6)' },
});
