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

const STRENGTHS = [
  { icon: 'checkmark-circle', text: 'Keyword Optimization', detail: 'Includes 85% of relevant industry terms.' },
  { icon: 'checkmark-circle', text: 'Clear Formatting', detail: 'Good parallels hierarchy and layout.' },
  { icon: 'checkmark-circle', text: 'Quantifiable Impact', detail: 'Strong use of metrics in experience section.' },
];

const IMPROVEMENTS = [
  'Add more detail to the Professional Summary.',
  'Include "Cloud Architecture" as a primary skill.',
  'Shorten bullet points to max 2 lines for readability.',
];

export default function InterviewScreen() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'analysis' | 'setup'>('analysis');

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>ATS Analysis</Text>
        <Pressable>
          <Ionicons name="ellipsis-vertical" size={22} color={Colors.textSecondary} />
        </Pressable>
      </View>

      {/* Tab switcher */}
      <View style={styles.tabRow}>
        <Pressable
          style={[styles.tab, activeTab === 'analysis' && styles.tabActive]}
          onPress={() => setActiveTab('analysis')}
        >
          <Text style={[styles.tabText, activeTab === 'analysis' && styles.tabTextActive]}>CV Analysis</Text>
        </Pressable>
        <Pressable
          style={[styles.tab, activeTab === 'setup' && styles.tabActive]}
          onPress={() => setActiveTab('setup')}
        >
          <Text style={[styles.tabText, activeTab === 'setup' && styles.tabTextActive]}>Interview Setup</Text>
        </Pressable>
      </View>

      {activeTab === 'analysis' ? (
        <>
          {/* Upload CV */}
          <View style={styles.uploadCard}>
            <Ionicons name="cloud-upload" size={40} color={Colors.accent} />
            <Text style={styles.uploadTitle}>Upload CV</Text>
            <Text style={styles.uploadSubtitle}>PDF or DOCX (Max. 5MB)</Text>
            <Pressable style={styles.selectFileButton}>
              <Text style={styles.selectFileText}>Select File</Text>
            </Pressable>
          </View>

          {/* Score Circle */}
          <View style={styles.scoreContainer}>
            <View style={styles.scoreCircle}>
              <Text style={styles.scoreNumber}>85</Text>
              <Text style={styles.scoreLabel}>SCORE</Text>
            </View>
            <Text style={styles.scoreQuote}>
              "Your CV is in the top 10% for this role"
            </Text>
          </View>

          {/* Strengths */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="checkmark-circle" size={18} color={Colors.success} />
              <Text style={styles.sectionTitle}>STRENGTHS</Text>
            </View>
            {STRENGTHS.map((item, index) => (
              <View key={index} style={styles.strengthItem}>
                <Ionicons name="checkmark-circle" size={16} color={Colors.success} />
                <View style={styles.strengthText}>
                  <Text style={styles.strengthTitle}>{item.text}</Text>
                  <Text style={styles.strengthDetail}>{item.detail}</Text>
                </View>
              </View>
            ))}
          </View>

          {/* Improvements */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="alert-circle" size={18} color={Colors.warning} />
              <Text style={styles.sectionTitle}>IMPROVEMENTS</Text>
            </View>
            {IMPROVEMENTS.map((text, index) => (
              <View key={index} style={styles.improvementItem}>
                <Text style={styles.bullet}>•</Text>
                <Text style={styles.improvementText}>{text}</Text>
              </View>
            ))}
          </View>

          {/* Action buttons */}
          <Pressable style={styles.primaryButton}>
            <Ionicons name="sparkles" size={20} color={Colors.textWhite} />
            <Text style={styles.primaryButtonText}>Improve CV with AI</Text>
          </Pressable>
          <Pressable style={styles.secondaryButton}>
            <Ionicons name="chatbubbles" size={20} color={Colors.primary} />
            <Text style={styles.secondaryButtonText}>Proceed to AI Interview</Text>
          </Pressable>
        </>
      ) : (
        /* Interview Setup Tab */
        <>
          {/* Job info */}
          <View style={styles.setupJobCard}>
            <View style={[styles.setupJobIcon, { backgroundColor: Colors.error }]}>
              <Ionicons name="briefcase" size={20} color={Colors.textWhite} />
            </View>
            <View>
              <Text style={styles.setupJobTitle}>Senior Product Designer</Text>
              <Text style={styles.setupJobCompany}>TechFlow Systems • AI Assessment</Text>
            </View>
          </View>

          {/* Interview Type */}
          <View style={styles.setupSection}>
            <View style={styles.setupSectionHeader}>
              <Ionicons name="chatbox" size={18} color={Colors.primary} />
              <Text style={styles.setupSectionTitle}>Interview Type</Text>
            </View>
            <View style={styles.optionRow}>
              <Pressable style={[styles.optionPill, styles.optionPillActive]}>
                <Text style={styles.optionPillTextActive}>Text Chat</Text>
              </Pressable>
              <Pressable style={styles.optionPill}>
                <Text style={styles.optionPillText}>Voice Call</Text>
              </Pressable>
            </View>
          </View>

          {/* Number of Questions */}
          <View style={styles.setupSection}>
            <View style={styles.setupSectionHeader}>
              <Ionicons name="help-circle" size={18} color={Colors.primary} />
              <Text style={styles.setupSectionTitle}>Number of Questions</Text>
            </View>
            <View style={styles.optionRow}>
              {['5 Qs', '10 Qs', '15 Qs'].map((q, i) => (
                <Pressable key={q} style={[styles.optionPill, i === 0 && styles.optionPillActive]}>
                  <Text style={[styles.optionPillText, i === 0 && styles.optionPillTextActive]}>{q}</Text>
                </Pressable>
              ))}
            </View>
          </View>

          {/* Difficulty */}
          <View style={styles.setupSection}>
            <View style={styles.setupSectionHeader}>
              <Ionicons name="speedometer" size={18} color={Colors.primary} />
              <Text style={styles.setupSectionTitle}>Difficulty Level</Text>
            </View>
            <View style={styles.optionRow}>
              {['Easy', 'Medium', 'Hard'].map((d, i) => (
                <Pressable key={d} style={[styles.optionPill, i === 1 && styles.optionPillActive]}>
                  <Text style={[styles.optionPillText, i === 1 && styles.optionPillTextActive]}>{d}</Text>
                </Pressable>
              ))}
            </View>
          </View>

          {/* Start button */}
          <Pressable style={styles.primaryButton}>
            <Text style={styles.primaryButtonText}>Start Interview</Text>
            <Ionicons name="mic" size={20} color={Colors.textWhite} />
          </Pressable>
          <Text style={styles.durationNote}>Average duration 15-20 minutes.</Text>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { paddingTop: 56, paddingHorizontal: Spacing.xxl, paddingBottom: 32 },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    marginBottom: Spacing.xl,
  },
  headerTitle: { fontSize: FontSize.xxl, fontWeight: FontWeight.bold, color: Colors.textPrimary },

  tabRow: { flexDirection: 'row', backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.md, padding: 4, marginBottom: Spacing.xxl },
  tab: { flex: 1, paddingVertical: Spacing.md, borderRadius: BorderRadius.sm, alignItems: 'center' },
  tabActive: { backgroundColor: Colors.background, ...Shadows.sm },
  tabText: { fontSize: FontSize.md, fontWeight: FontWeight.medium, color: Colors.textSecondary },
  tabTextActive: { color: Colors.primary, fontWeight: FontWeight.semibold },

  uploadCard: {
    alignItems: 'center', borderWidth: 2, borderColor: Colors.border, borderStyle: 'dashed',
    borderRadius: BorderRadius.lg, padding: Spacing.xxl, gap: Spacing.sm, marginBottom: Spacing.xxl,
  },
  uploadTitle: { fontSize: FontSize.lg, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  uploadSubtitle: { fontSize: FontSize.sm, color: Colors.textTertiary },
  selectFileButton: {
    backgroundColor: Colors.primary, borderRadius: BorderRadius.sm, paddingHorizontal: Spacing.xxl,
    paddingVertical: Spacing.md, marginTop: Spacing.md,
  },
  selectFileText: { fontSize: FontSize.md, fontWeight: FontWeight.semibold, color: Colors.textWhite },

  scoreContainer: { alignItems: 'center', marginBottom: Spacing.xxl },
  scoreCircle: {
    width: 120, height: 120, borderRadius: 60, borderWidth: 6, borderColor: Colors.primary,
    justifyContent: 'center', alignItems: 'center', marginBottom: Spacing.lg,
  },
  scoreNumber: { fontSize: 40, fontWeight: FontWeight.extrabold, color: Colors.primary },
  scoreLabel: { fontSize: FontSize.xs, fontWeight: FontWeight.semibold, color: Colors.textSecondary, letterSpacing: 1 },
  scoreQuote: { fontSize: FontSize.sm, color: Colors.textSecondary, fontStyle: 'italic', textAlign: 'center' },

  section: { marginBottom: Spacing.xxl },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.lg },
  sectionTitle: { fontSize: FontSize.sm, fontWeight: FontWeight.bold, color: Colors.textPrimary, letterSpacing: 0.5 },

  strengthItem: { flexDirection: 'row', gap: Spacing.md, marginBottom: Spacing.lg, alignItems: 'flex-start' },
  strengthText: { flex: 1 },
  strengthTitle: { fontSize: FontSize.md, fontWeight: FontWeight.semibold, color: Colors.textPrimary, marginBottom: 2 },
  strengthDetail: { fontSize: FontSize.sm, color: Colors.textSecondary, lineHeight: 18 },

  improvementItem: { flexDirection: 'row', gap: Spacing.sm, marginBottom: Spacing.md },
  bullet: { fontSize: FontSize.lg, color: Colors.textSecondary },
  improvementText: { flex: 1, fontSize: FontSize.sm, color: Colors.textSecondary, lineHeight: 18 },

  primaryButton: {
    backgroundColor: Colors.primary, borderRadius: BorderRadius.xl, paddingVertical: Spacing.lg + 2,
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.md,
  },
  primaryButtonText: { color: Colors.textWhite, fontSize: FontSize.xl, fontWeight: FontWeight.semibold },
  secondaryButton: {
    borderWidth: 1.5, borderColor: Colors.primary, borderRadius: BorderRadius.xl, paddingVertical: Spacing.lg + 2,
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.md,
  },
  secondaryButtonText: { color: Colors.primary, fontSize: FontSize.xl, fontWeight: FontWeight.semibold },

  setupJobCard: {
    flexDirection: 'row', alignItems: 'center', gap: Spacing.lg,
    backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.lg, padding: Spacing.lg, marginBottom: Spacing.xxl,
  },
  setupJobIcon: { width: 44, height: 44, borderRadius: BorderRadius.md, justifyContent: 'center', alignItems: 'center' },
  setupJobTitle: { fontSize: FontSize.lg, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  setupJobCompany: { fontSize: FontSize.sm, color: Colors.textSecondary },

  setupSection: { marginBottom: Spacing.xxl },
  setupSectionHeader: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.lg },
  setupSectionTitle: { fontSize: FontSize.lg, fontWeight: FontWeight.bold, color: Colors.textPrimary },

  optionRow: { flexDirection: 'row', gap: Spacing.md },
  optionPill: {
    flex: 1, alignItems: 'center', paddingVertical: Spacing.md, borderWidth: 1, borderColor: Colors.border,
    borderRadius: BorderRadius.md, backgroundColor: Colors.background,
  },
  optionPillActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  optionPillText: { fontSize: FontSize.md, fontWeight: FontWeight.medium, color: Colors.textSecondary },
  optionPillTextActive: { color: Colors.textWhite, fontWeight: FontWeight.semibold },

  durationNote: { fontSize: FontSize.sm, color: Colors.textTertiary, textAlign: 'center', marginTop: Spacing.sm },
});
