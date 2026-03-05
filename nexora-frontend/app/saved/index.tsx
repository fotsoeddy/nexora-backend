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

const SAVED_JOBS = [
  { id: '1', title: 'Senior AI Engineer', company: 'OpenAI', location: 'San Francisco', salary: '$200K - $280K', saved: '1 day ago', iconBg: '#3B82F6', tags: ['Python', 'LLM', 'Remote'] },
  { id: '2', title: 'Product Designer', company: 'Figma', location: 'New York', salary: '$150K - $190K', saved: '3 days ago', iconBg: '#8B5CF6', tags: ['Figma', 'UI/UX', 'Hybrid'] },
  { id: '3', title: 'DevOps Engineer', company: 'Vercel', location: 'Remote', salary: '$140K - $180K', saved: '1 week ago', iconBg: '#10B981', tags: ['AWS', 'Docker', 'CI/CD'] },
  { id: '4', title: 'Data Analyst', company: 'Spotify', location: 'Stockholm', salary: '€65K - €90K', saved: '2 weeks ago', iconBg: '#EC4899', tags: ['SQL', 'Python', 'Tableau'] },
];

export default function SavedJobsScreen() {
  const router = useRouter();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
        </Pressable>
        <Text style={styles.headerTitle}>Saved Jobs</Text>
        <Text style={styles.countText}>{SAVED_JOBS.length} saved</Text>
      </View>

      {SAVED_JOBS.map((job) => (
        <Pressable key={job.id} style={styles.jobCard} onPress={() => router.push(`/job/${job.id}`)}>
          <View style={styles.jobHeader}>
            <View style={[styles.jobIcon, { backgroundColor: job.iconBg }]}>
              <Ionicons name="business" size={20} color={Colors.textWhite} />
            </View>
            <View style={styles.jobInfo}>
              <Text style={styles.jobTitle}>{job.title}</Text>
              <Text style={styles.jobCompany}>{job.company} • {job.location}</Text>
            </View>
            <Pressable style={styles.bookmarkBtn}>
              <Ionicons name="bookmark" size={20} color={Colors.accent} />
            </Pressable>
          </View>

          <View style={styles.tagsRow}>
            {job.tags.map((tag, i) => (
              <View key={i} style={styles.tag}>
                <Text style={styles.tagText}>{tag}</Text>
              </View>
            ))}
          </View>

          <View style={styles.jobFooter}>
            <Text style={styles.salary}>{job.salary}</Text>
            <Text style={styles.savedText}>Saved {job.saved}</Text>
          </View>

          <View style={styles.actionRow}>
            <Pressable style={styles.applyBtn}>
              <Ionicons name="send" size={16} color={Colors.textWhite} />
              <Text style={styles.applyBtnText}>Quick Apply</Text>
            </Pressable>
            <Pressable style={styles.atsBtn}>
              <Ionicons name="document-text" size={16} color={Colors.accent} />
              <Text style={styles.atsBtnText}>ATS Check</Text>
            </Pressable>
          </View>
        </Pressable>
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
  countText: { fontSize: FontSize.sm, fontWeight: FontWeight.medium, color: Colors.textSecondary },

  jobCard: {
    backgroundColor: Colors.background, borderWidth: 1, borderColor: Colors.borderLight,
    borderRadius: BorderRadius.lg, padding: Spacing.lg, marginBottom: Spacing.md,
    gap: Spacing.md, ...Shadows.sm,
  },
  jobHeader: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  jobIcon: { width: 44, height: 44, borderRadius: BorderRadius.md, justifyContent: 'center', alignItems: 'center' },
  jobInfo: { flex: 1, gap: 2 },
  jobTitle: { fontSize: FontSize.lg, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  jobCompany: { fontSize: FontSize.sm, color: Colors.textSecondary },
  bookmarkBtn: { padding: Spacing.xs },

  tagsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  tag: { backgroundColor: Colors.backgroundTertiary, borderRadius: 6, paddingHorizontal: Spacing.md, paddingVertical: 4 },
  tagText: { fontSize: FontSize.xs, fontWeight: FontWeight.semibold, color: Colors.textSecondary },

  jobFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  salary: { fontSize: FontSize.lg, fontWeight: FontWeight.bold, color: Colors.primary },
  savedText: { fontSize: FontSize.xs, color: Colors.textTertiary },

  actionRow: { flexDirection: 'row', gap: Spacing.md },
  applyBtn: {
    flex: 1, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: Spacing.sm,
    backgroundColor: Colors.primary, borderRadius: BorderRadius.md, paddingVertical: Spacing.md,
  },
  applyBtnText: { fontSize: FontSize.sm, fontWeight: FontWeight.semibold, color: Colors.textWhite },
  atsBtn: {
    flex: 1, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: Spacing.sm,
    borderWidth: 1, borderColor: Colors.accent, borderRadius: BorderRadius.md, paddingVertical: Spacing.md,
  },
  atsBtnText: { fontSize: FontSize.sm, fontWeight: FontWeight.semibold, color: Colors.accent },
});
