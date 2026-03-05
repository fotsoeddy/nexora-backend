import React, { useState } from 'react';
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
import { Colors, FontSize, FontWeight, Spacing, BorderRadius } from '../../src/constants/theme';

const LOCATION_DATA = [
  { city: 'San Francisco', range: '$160K - $220K', diff: '+35%' },
  { city: 'New York', range: '$150K - $200K', diff: '+28%' },
  { city: 'London', range: '£90K - £140K', diff: '+15%' },
  { city: 'Paris', range: '€65K - €95K', diff: '+5%' },
  { city: 'Douala', range: 'XAF 8M - 15M', diff: 'Base' },
];

const FACTORS = [
  { label: 'Experience Level', value: 'Senior (5-8 yrs)', icon: 'trending-up', color: Colors.success },
  { label: 'Industry', value: 'Tech / AI', icon: 'hardware-chip', color: Colors.accent },
  { label: 'Company Size', value: '200-1000', icon: 'business', color: Colors.warning },
  { label: 'Remote Status', value: 'Hybrid', icon: 'globe', color: Colors.info },
];

export default function SalaryScreen() {
  const router = useRouter();
  const [jobTitle, setJobTitle] = useState('AI Solutions Architect');
  const [showResults, setShowResults] = useState(false);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
        </Pressable>
        <Text style={styles.headerTitle}>Salary Estimator</Text>
        <View style={styles.aiBadge}>
          <Ionicons name="sparkles" size={12} color={Colors.textWhite} />
          <Text style={styles.aiBadgeText}>AI</Text>
        </View>
      </View>

      {!showResults ? (
        <>
          <View style={styles.heroCard}>
            <View style={styles.heroIconCircle}>
              <Ionicons name="cash" size={32} color={Colors.success} />
            </View>
            <Text style={styles.heroTitle}>Know Your Worth</Text>
            <Text style={styles.heroSubtitle}>
              Get an AI-powered salary estimate based on your role, experience, location,
              and industry trends.
            </Text>
          </View>

          <View style={styles.form}>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Job Title</Text>
              <View style={styles.inputContainer}>
                <Ionicons name="briefcase-outline" size={18} color={Colors.textTertiary} />
                <TextInput
                  style={styles.input}
                  value={jobTitle}
                  onChangeText={setJobTitle}
                  placeholder="e.g. Data Scientist"
                  placeholderTextColor={Colors.textTertiary}
                />
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Location</Text>
              <View style={styles.inputContainer}>
                <Ionicons name="location-outline" size={18} color={Colors.textTertiary} />
                <TextInput
                  style={styles.input}
                  placeholder="e.g. Paris, France"
                  placeholderTextColor={Colors.textTertiary}
                />
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Experience (years)</Text>
              <View style={styles.expRow}>
                {['0-2', '3-5', '5-8', '8+'].map((exp, i) => (
                  <Pressable key={exp} style={[styles.expChip, i === 2 && styles.expChipActive]}>
                    <Text style={[styles.expText, i === 2 && styles.expTextActive]}>{exp}</Text>
                  </Pressable>
                ))}
              </View>
            </View>
          </View>

          <Pressable style={styles.primaryButton} onPress={() => setShowResults(true)}>
            <Ionicons name="analytics" size={20} color={Colors.textWhite} />
            <Text style={styles.primaryButtonText}>Estimate Salary</Text>
          </Pressable>
        </>
      ) : (
        <>
          {/* Result */}
          <View style={styles.resultCard}>
            <Text style={styles.resultLabel}>ESTIMATED SALARY RANGE</Text>
            <Text style={styles.resultTitle}>{jobTitle}</Text>
            <View style={styles.resultRange}>
              <Text style={styles.rangeMin}>$140K</Text>
              <View style={styles.rangeLine}>
                <View style={styles.rangeIndicator} />
              </View>
              <Text style={styles.rangeMax}>$200K</Text>
            </View>
            <Text style={styles.resultMedian}>Median: $168K / year</Text>
            <Text style={styles.resultNote}>Based on 1,247 data points from similar roles</Text>
          </View>

          {/* Factors */}
          <Text style={styles.sectionTitle}>Contributing Factors</Text>
          <View style={styles.factorsGrid}>
            {FACTORS.map((f, i) => (
              <View key={i} style={styles.factorCard}>
                <View style={[styles.factorIcon, { backgroundColor: f.color + '15' }]}>
                  <Ionicons name={f.icon as any} size={18} color={f.color} />
                </View>
                <Text style={styles.factorLabel}>{f.label}</Text>
                <Text style={styles.factorValue}>{f.value}</Text>
              </View>
            ))}
          </View>

          {/* By Location */}
          <Text style={styles.sectionTitle}>Salary by Location</Text>
          <View style={styles.locationList}>
            {LOCATION_DATA.map((l, i) => (
              <View key={i} style={styles.locationItem}>
                <View style={styles.locationInfo}>
                  <Ionicons name="location" size={16} color={Colors.accent} />
                  <Text style={styles.locationCity}>{l.city}</Text>
                </View>
                <View style={styles.locationRight}>
                  <Text style={styles.locationRange}>{l.range}</Text>
                  <Text style={[styles.locationDiff, l.diff !== 'Base' && { color: Colors.success }]}>
                    {l.diff}
                  </Text>
                </View>
              </View>
            ))}
          </View>

          {/* Tips */}
          <View style={styles.tipCard}>
            <Ionicons name="bulb" size={20} color={Colors.warning} />
            <View style={{ flex: 1 }}>
              <Text style={styles.tipTitle}>Negotiation Tip</Text>
              <Text style={styles.tipText}>
                Ask for 10-15% above the median. Companies often have budget flexibility for strong candidates.
              </Text>
            </View>
          </View>

          <Pressable style={styles.secondaryButton} onPress={() => setShowResults(false)}>
            <Ionicons name="refresh" size={20} color={Colors.primary} />
            <Text style={styles.secondaryButtonText}>New Estimation</Text>
          </Pressable>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { paddingTop: 52, paddingHorizontal: Spacing.xxl, paddingBottom: 40 },

  header: {
    flexDirection: 'row', alignItems: 'center', marginBottom: Spacing.xxl, gap: Spacing.md,
  },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { flex: 1, fontSize: FontSize.xxl, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  aiBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: Colors.accent,
    borderRadius: BorderRadius.full, paddingHorizontal: Spacing.md, paddingVertical: 4,
  },
  aiBadgeText: { fontSize: FontSize.xs, fontWeight: FontWeight.bold, color: Colors.textWhite },

  heroCard: {
    backgroundColor: Colors.success + '08', borderRadius: BorderRadius.lg, borderWidth: 1,
    borderColor: Colors.success + '20', padding: Spacing.xxl, alignItems: 'center',
    marginBottom: Spacing.xxl,
  },
  heroIconCircle: {
    width: 64, height: 64, borderRadius: 32, backgroundColor: Colors.success + '15',
    justifyContent: 'center', alignItems: 'center', marginBottom: Spacing.lg,
  },
  heroTitle: { fontSize: FontSize.xxl, fontWeight: FontWeight.bold, color: Colors.textPrimary, marginBottom: Spacing.sm },
  heroSubtitle: { fontSize: FontSize.md, color: Colors.textSecondary, textAlign: 'center', lineHeight: 22 },

  form: { gap: Spacing.xl, marginBottom: Spacing.xxl },
  inputGroup: { gap: Spacing.sm },
  label: { fontSize: FontSize.md, fontWeight: FontWeight.semibold, color: Colors.textPrimary },
  inputContainer: {
    flexDirection: 'row', alignItems: 'center', borderWidth: 1, borderColor: Colors.border,
    borderRadius: BorderRadius.md, paddingHorizontal: Spacing.lg, height: 52, gap: Spacing.md,
  },
  input: { flex: 1, fontSize: FontSize.md, color: Colors.textPrimary },

  expRow: { flexDirection: 'row', gap: Spacing.md },
  expChip: {
    flex: 1, alignItems: 'center', paddingVertical: Spacing.md, borderWidth: 1,
    borderColor: Colors.border, borderRadius: BorderRadius.md,
  },
  expChipActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  expText: { fontSize: FontSize.md, fontWeight: FontWeight.medium, color: Colors.textSecondary },
  expTextActive: { color: Colors.textWhite, fontWeight: FontWeight.semibold },

  resultCard: {
    backgroundColor: Colors.primary, borderRadius: BorderRadius.lg,
    padding: Spacing.xxl, alignItems: 'center', marginBottom: Spacing.xxl,
  },
  resultLabel: { fontSize: FontSize.xs, letterSpacing: 1, color: 'rgba(255,255,255,0.5)', fontWeight: FontWeight.bold, marginBottom: Spacing.sm },
  resultTitle: { fontSize: FontSize.xl, fontWeight: FontWeight.bold, color: Colors.textWhite, marginBottom: Spacing.xl },
  resultRange: { flexDirection: 'row', alignItems: 'center', gap: Spacing.lg, marginBottom: Spacing.lg, width: '100%' },
  rangeMin: { fontSize: FontSize.xl, fontWeight: FontWeight.extrabold, color: Colors.textWhite },
  rangeLine: { flex: 1, height: 6, backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 3 },
  rangeIndicator: { width: '65%', height: 6, backgroundColor: Colors.success, borderRadius: 3 },
  rangeMax: { fontSize: FontSize.xl, fontWeight: FontWeight.extrabold, color: Colors.textWhite },
  resultMedian: { fontSize: FontSize.lg, fontWeight: FontWeight.semibold, color: Colors.success, marginBottom: 4 },
  resultNote: { fontSize: FontSize.xs, color: 'rgba(255,255,255,0.5)' },

  sectionTitle: { fontSize: FontSize.xl, fontWeight: FontWeight.bold, color: Colors.textPrimary, marginBottom: Spacing.lg },

  factorsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.md, marginBottom: Spacing.xxl },
  factorCard: {
    width: '47%', backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.md,
    padding: Spacing.lg, gap: 4,
  },
  factorIcon: { width: 36, height: 36, borderRadius: BorderRadius.sm, justifyContent: 'center', alignItems: 'center', marginBottom: 4 },
  factorLabel: { fontSize: FontSize.xs, color: Colors.textSecondary },
  factorValue: { fontSize: FontSize.md, fontWeight: FontWeight.bold, color: Colors.textPrimary },

  locationList: { marginBottom: Spacing.xxl },
  locationItem: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingVertical: Spacing.lg, borderBottomWidth: 1, borderBottomColor: Colors.borderLight,
  },
  locationInfo: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  locationCity: { fontSize: FontSize.md, fontWeight: FontWeight.medium, color: Colors.textPrimary },
  locationRight: { alignItems: 'flex-end' },
  locationRange: { fontSize: FontSize.md, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  locationDiff: { fontSize: FontSize.xs, color: Colors.textSecondary, fontWeight: FontWeight.medium },

  tipCard: {
    flexDirection: 'row', gap: Spacing.lg, backgroundColor: Colors.warningLight,
    borderRadius: BorderRadius.md, padding: Spacing.lg, marginBottom: Spacing.xxl,
  },
  tipTitle: { fontSize: FontSize.md, fontWeight: FontWeight.bold, color: Colors.textPrimary, marginBottom: 2 },
  tipText: { fontSize: FontSize.sm, color: Colors.textSecondary, lineHeight: 18 },

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
