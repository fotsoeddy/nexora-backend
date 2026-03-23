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
import { Colors, FontSize, FontWeight, Spacing, BorderRadius, Shadows } from '../../src/constants/theme';

const STRENGTHS = [
  'Clear and structured communication',
  'Strong technical problem-solving',
  'Effective use of STAR method',
  'Excellent leadership examples',
];

const IMPROVEMENTS = [
  'Provide more quantifiable impact metrics',
  'Elaborate on conflict resolution strategies',
  'Add detail about scalability considerations',
];

const STRATEGIES = [
  { icon: 'book', text: 'Review system design fundamentals', color: Colors.accent },
  { icon: 'people', text: 'Practice behavioral questions', color: Colors.success },
  { icon: 'timer', text: 'Work on concise responses', color: Colors.warning },
];

export default function InterviewResultScreen() {
  const router = useRouter();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
        </Pressable>
        <Text style={styles.headerTitle}>Interview Result</Text>
        <Pressable>
          <Ionicons name="share-outline" size={22} color={Colors.textPrimary} />
        </Pressable>
      </View>

      {/* Score */}
      <View style={styles.scoreSection}>
        <View style={styles.scoreCircle}>
          <Text style={styles.scoreNumber}>85</Text>
          <Text style={styles.scoreMax}>/100</Text>
        </View>
        <Text style={styles.scoreLabel}>Excellent Performance</Text>
        <Text style={styles.scoreDescription}>
          You performed above average compared to other candidates for this role.
        </Text>
      </View>

      {/* Stats row */}
      <View style={styles.statsRow}>
        <View style={styles.statCard}>
          <Ionicons name="chatbubble" size={18} color={Colors.accent} />
          <Text style={styles.statNumber}>10</Text>
          <Text style={styles.statLabel}>Questions</Text>
        </View>
        <View style={styles.statCard}>
          <Ionicons name="time" size={18} color={Colors.warning} />
          <Text style={styles.statNumber}>18m</Text>
          <Text style={styles.statLabel}>Duration</Text>
        </View>
        <View style={styles.statCard}>
          <Ionicons name="trending-up" size={18} color={Colors.success} />
          <Text style={styles.statNumber}>Top 15%</Text>
          <Text style={styles.statLabel}>Ranking</Text>
        </View>
      </View>

      {/* Strengths */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <View style={[styles.sectionIcon, { backgroundColor: Colors.success + '15' }]}>
            <Ionicons name="checkmark-circle" size={18} color={Colors.success} />
          </View>
          <Text style={styles.sectionTitle}>Strengths</Text>
        </View>
        {STRENGTHS.map((item, index) => (
          <View key={index} style={styles.listItem}>
            <Ionicons name="checkmark" size={16} color={Colors.success} />
            <Text style={styles.listText}>{item}</Text>
          </View>
        ))}
      </View>

      {/* Improvements */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <View style={[styles.sectionIcon, { backgroundColor: Colors.warning + '15' }]}>
            <Ionicons name="alert-circle" size={18} color={Colors.warning} />
          </View>
          <Text style={styles.sectionTitle}>Areas for Improvement</Text>
        </View>
        {IMPROVEMENTS.map((item, index) => (
          <View key={index} style={styles.listItem}>
            <Ionicons name="arrow-forward" size={14} color={Colors.warning} />
            <Text style={styles.listText}>{item}</Text>
          </View>
        ))}
      </View>

      {/* Suggested Strategy */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <View style={[styles.sectionIcon, { backgroundColor: Colors.accent + '15' }]}>
            <Ionicons name="bulb" size={18} color={Colors.accent} />
          </View>
          <Text style={styles.sectionTitle}>Suggested Strategy</Text>
        </View>
        {STRATEGIES.map((item, index) => (
          <View key={index} style={styles.strategyItem}>
            <View style={[styles.strategyIcon, { backgroundColor: item.color + '15' }]}>
              <Ionicons name={item.icon as any} size={18} color={item.color} />
            </View>
            <Text style={styles.strategyText}>{item.text}</Text>
          </View>
        ))}
      </View>

      {/* Action buttons */}
      <View style={styles.actions}>
        <Pressable style={styles.primaryButton}>
          <Ionicons name="refresh" size={20} color={Colors.textWhite} />
          <Text style={styles.primaryButtonText}>Retry Interview</Text>
        </Pressable>
        <Pressable style={styles.secondaryButton}>
          <Ionicons name="download" size={20} color={Colors.primary} />
          <Text style={styles.secondaryButtonText}>Download Report</Text>
        </Pressable>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { paddingTop: 52, paddingBottom: 40 },

  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: Spacing.xxl, marginBottom: Spacing.xxl,
  },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { fontSize: FontSize.xl, fontWeight: FontWeight.bold, color: Colors.textPrimary },

  scoreSection: { alignItems: 'center', paddingHorizontal: Spacing.xxl, marginBottom: Spacing.xxl },
  scoreCircle: {
    width: 140, height: 140, borderRadius: 70, borderWidth: 8, borderColor: Colors.success,
    justifyContent: 'center', alignItems: 'center', marginBottom: Spacing.lg,
    backgroundColor: Colors.success + '08',
  },
  scoreNumber: { fontSize: 48, fontWeight: FontWeight.extrabold, color: Colors.success },
  scoreMax: { fontSize: FontSize.md, color: Colors.textSecondary, fontWeight: FontWeight.medium, marginTop: -4 },
  scoreLabel: { fontSize: FontSize.xxl, fontWeight: FontWeight.bold, color: Colors.textPrimary, marginBottom: Spacing.sm },
  scoreDescription: { fontSize: FontSize.md, color: Colors.textSecondary, textAlign: 'center', lineHeight: 22 },

  statsRow: {
    flexDirection: 'row', paddingHorizontal: Spacing.xxl, gap: Spacing.md,
    marginBottom: Spacing.xxl,
  },
  statCard: {
    flex: 1, backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.lg,
    padding: Spacing.lg, alignItems: 'center', gap: 4,
  },
  statNumber: { fontSize: FontSize.xl, fontWeight: FontWeight.extrabold, color: Colors.textPrimary },
  statLabel: { fontSize: FontSize.xs, color: Colors.textSecondary },

  section: { paddingHorizontal: Spacing.xxl, marginBottom: Spacing.xxl },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md, marginBottom: Spacing.lg },
  sectionIcon: { width: 32, height: 32, borderRadius: 16, justifyContent: 'center', alignItems: 'center' },
  sectionTitle: { fontSize: FontSize.xl, fontWeight: FontWeight.bold, color: Colors.textPrimary },

  listItem: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md, marginBottom: Spacing.md, paddingLeft: Spacing.xs },
  listText: { flex: 1, fontSize: FontSize.md, color: Colors.textSecondary, lineHeight: 22 },

  strategyItem: {
    flexDirection: 'row', alignItems: 'center', gap: Spacing.lg,
    backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.md,
    padding: Spacing.lg, marginBottom: Spacing.md,
  },
  strategyIcon: { width: 40, height: 40, borderRadius: BorderRadius.md, justifyContent: 'center', alignItems: 'center' },
  strategyText: { flex: 1, fontSize: FontSize.md, fontWeight: FontWeight.medium, color: Colors.textPrimary },

  actions: { paddingHorizontal: Spacing.xxl, gap: Spacing.md },
  primaryButton: {
    backgroundColor: Colors.primary, borderRadius: BorderRadius.xl, paddingVertical: Spacing.lg + 2,
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: Spacing.sm,
  },
  primaryButtonText: { color: Colors.textWhite, fontSize: FontSize.xl, fontWeight: FontWeight.semibold },
  secondaryButton: {
    borderWidth: 1.5, borderColor: Colors.primary, borderRadius: BorderRadius.xl,
    paddingVertical: Spacing.lg + 2, flexDirection: 'row', justifyContent: 'center',
    alignItems: 'center', gap: Spacing.sm,
  },
  secondaryButtonText: { color: Colors.primary, fontSize: FontSize.xl, fontWeight: FontWeight.semibold },
});
