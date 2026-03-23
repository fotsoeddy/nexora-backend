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
import { Colors, FontSize, FontWeight, Spacing, BorderRadius, Shadows } from '../../src/constants/theme';

const GENERATED_LETTER = `Dear Hiring Manager,

I am writing to express my strong interest in the Lead AI Solutions Architect position at NeuralStream AI. With over 6 years of experience in designing and deploying scalable machine learning systems, I am confident that my skills align perfectly with your requirements.

In my current role at TechFlow Systems, I successfully led a team of engineers to migrate our ML infrastructure to a cloud-native architecture, reducing inference latency by 40% and cutting operational costs by 30%.

I am particularly drawn to NeuralStream AI's mission to democratize enterprise AI solutions. My experience with LLM deployment, distributed systems, and cross-functional leadership positions me to make an immediate impact on your team.

I look forward to discussing how my background can contribute to NeuralStream AI's continued growth. Thank you for your consideration.

Best regards,
Eddy Fotso`;

export default function CoverLetterScreen() {
  const router = useRouter();
  const [jobTitle, setJobTitle] = useState('Lead AI Solutions Architect');
  const [company, setCompany] = useState('NeuralStream AI');
  const [isGenerated, setIsGenerated] = useState(false);
  const [tone, setTone] = useState('Professional');

  const tones = ['Professional', 'Confident', 'Creative', 'Formal'];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
        </Pressable>
        <Text style={styles.headerTitle}>Cover Letter</Text>
        <View style={styles.aiBadge}>
          <Ionicons name="sparkles" size={12} color={Colors.textWhite} />
          <Text style={styles.aiBadgeText}>AI</Text>
        </View>
      </View>

      {!isGenerated ? (
        <>
          {/* Input form */}
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Ionicons name="create" size={22} color={Colors.accent} />
              <Text style={styles.cardTitle}>Generate Cover Letter</Text>
            </View>
            <Text style={styles.cardSubtitle}>
              Fill in the details and our AI will craft a personalized, professional cover letter.
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
                  placeholder="e.g. Senior Developer"
                  placeholderTextColor={Colors.textTertiary}
                />
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Company Name</Text>
              <View style={styles.inputContainer}>
                <Ionicons name="business-outline" size={18} color={Colors.textTertiary} />
                <TextInput
                  style={styles.input}
                  value={company}
                  onChangeText={setCompany}
                  placeholder="e.g. Google"
                  placeholderTextColor={Colors.textTertiary}
                />
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Tone</Text>
              <View style={styles.toneRow}>
                {tones.map((t) => (
                  <Pressable
                    key={t}
                    style={[styles.toneChip, tone === t && styles.toneChipActive]}
                    onPress={() => setTone(t)}
                  >
                    <Text style={[styles.toneText, tone === t && styles.toneTextActive]}>{t}</Text>
                  </Pressable>
                ))}
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Additional Notes (optional)</Text>
              <View style={[styles.inputContainer, { height: 80, alignItems: 'flex-start', paddingVertical: Spacing.md }]}>
                <TextInput
                  style={[styles.input, { textAlignVertical: 'top' }]}
                  placeholder="Mention specific skills or achievements..."
                  placeholderTextColor={Colors.textTertiary}
                  multiline
                />
              </View>
            </View>
          </View>

          <Pressable style={styles.primaryButton} onPress={() => setIsGenerated(true)}>
            <Ionicons name="sparkles" size={20} color={Colors.textWhite} />
            <Text style={styles.primaryButtonText}>Generate with AI</Text>
          </Pressable>
        </>
      ) : (
        <>
          {/* Generated letter */}
          <View style={styles.successBanner}>
            <Ionicons name="checkmark-circle" size={20} color={Colors.success} />
            <Text style={styles.successText}>Cover letter generated successfully!</Text>
          </View>

          <View style={styles.letterCard}>
            <View style={styles.letterHeader}>
              <Text style={styles.letterTarget}>{jobTitle}</Text>
              <Text style={styles.letterCompany}>{company} • {tone} tone</Text>
            </View>
            <View style={styles.letterDivider} />
            <Text style={styles.letterContent}>{GENERATED_LETTER}</Text>
          </View>

          {/* Actions */}
          <View style={styles.actionRow}>
            <Pressable style={styles.actionBtn}>
              <Ionicons name="copy-outline" size={20} color={Colors.accent} />
              <Text style={styles.actionBtnText}>Copy</Text>
            </Pressable>
            <Pressable style={styles.actionBtn}>
              <Ionicons name="download-outline" size={20} color={Colors.accent} />
              <Text style={styles.actionBtnText}>Download</Text>
            </Pressable>
            <Pressable style={styles.actionBtn}>
              <Ionicons name="share-outline" size={20} color={Colors.accent} />
              <Text style={styles.actionBtnText}>Share</Text>
            </Pressable>
          </View>

          <Pressable style={styles.primaryButton} onPress={() => setIsGenerated(false)}>
            <Ionicons name="refresh" size={20} color={Colors.textWhite} />
            <Text style={styles.primaryButtonText}>Regenerate</Text>
          </Pressable>
          <Pressable style={styles.secondaryButton}>
            <Ionicons name="create-outline" size={20} color={Colors.primary} />
            <Text style={styles.secondaryButtonText}>Edit Manually</Text>
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

  card: {
    backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.lg,
    padding: Spacing.xl, marginBottom: Spacing.xxl,
  },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md, marginBottom: Spacing.sm },
  cardTitle: { fontSize: FontSize.xl, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  cardSubtitle: { fontSize: FontSize.md, color: Colors.textSecondary, lineHeight: 22 },

  form: { gap: Spacing.xl, marginBottom: Spacing.xxl },
  inputGroup: { gap: Spacing.sm },
  label: { fontSize: FontSize.md, fontWeight: FontWeight.semibold, color: Colors.textPrimary },
  inputContainer: {
    flexDirection: 'row', alignItems: 'center', borderWidth: 1, borderColor: Colors.border,
    borderRadius: BorderRadius.md, paddingHorizontal: Spacing.lg, height: 52, gap: Spacing.md,
  },
  input: { flex: 1, fontSize: FontSize.md, color: Colors.textPrimary },

  toneRow: { flexDirection: 'row', gap: Spacing.sm, flexWrap: 'wrap' },
  toneChip: {
    borderWidth: 1, borderColor: Colors.border, borderRadius: BorderRadius.full,
    paddingHorizontal: Spacing.lg, paddingVertical: Spacing.sm + 2,
  },
  toneChipActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  toneText: { fontSize: FontSize.sm, fontWeight: FontWeight.medium, color: Colors.textSecondary },
  toneTextActive: { color: Colors.textWhite },

  successBanner: {
    flexDirection: 'row', alignItems: 'center', gap: Spacing.md,
    backgroundColor: Colors.successLight, borderRadius: BorderRadius.md,
    padding: Spacing.lg, marginBottom: Spacing.xxl,
  },
  successText: { fontSize: FontSize.md, fontWeight: FontWeight.semibold, color: Colors.success },

  letterCard: {
    backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.lg,
    padding: Spacing.xl, marginBottom: Spacing.xxl,
  },
  letterHeader: { marginBottom: Spacing.lg },
  letterTarget: { fontSize: FontSize.lg, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  letterCompany: { fontSize: FontSize.sm, color: Colors.textSecondary, marginTop: 2 },
  letterDivider: { height: 1, backgroundColor: Colors.border, marginBottom: Spacing.lg },
  letterContent: { fontSize: FontSize.md, color: Colors.textPrimary, lineHeight: 24 },

  actionRow: {
    flexDirection: 'row', justifyContent: 'center', gap: Spacing.xxl,
    marginBottom: Spacing.xxl,
  },
  actionBtn: { alignItems: 'center', gap: 4 },
  actionBtnText: { fontSize: FontSize.sm, color: Colors.accent, fontWeight: FontWeight.medium },

  primaryButton: {
    backgroundColor: Colors.primary, borderRadius: BorderRadius.xl, paddingVertical: Spacing.lg + 2,
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: Spacing.sm,
    marginBottom: Spacing.md,
  },
  primaryButtonText: { color: Colors.textWhite, fontSize: FontSize.xl, fontWeight: FontWeight.semibold },
  secondaryButton: {
    borderWidth: 1.5, borderColor: Colors.primary, borderRadius: BorderRadius.xl,
    paddingVertical: Spacing.lg + 2, flexDirection: 'row', justifyContent: 'center',
    alignItems: 'center', gap: Spacing.sm,
  },
  secondaryButtonText: { color: Colors.primary, fontSize: FontSize.xl, fontWeight: FontWeight.semibold },
});
