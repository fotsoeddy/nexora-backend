import React, { useState } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, FontWeight, Spacing, BorderRadius, Shadows } from '../../src/constants/theme';

const TABS = ['Overview', 'Requirements', 'Company'] as const;

export default function JobDetailScreen() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<typeof TABS[number]>('Overview');

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Pressable style={styles.backButton} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
          </Pressable>
          <Text style={styles.headerTitle}>Job Details</Text>
          <Pressable>
            <Ionicons name="share-outline" size={22} color={Colors.textPrimary} />
          </Pressable>
        </View>

        {/* Company info */}
        <View style={styles.companyCard}>
          <View style={styles.companyLogo}>
            <Ionicons name="business" size={28} color={Colors.textWhite} />
          </View>
          <Text style={styles.jobTitle}>Lead AI Solutions Architect</Text>
          <View style={styles.companyMeta}>
            <Ionicons name="business-outline" size={14} color={Colors.textSecondary} />
            <Text style={styles.companyText}>NeuralStream AI • Palo Alto, CA</Text>
          </View>
          <View style={styles.companyMeta}>
            <Ionicons name="time-outline" size={14} color={Colors.textSecondary} />
            <Text style={styles.companyText}>Posted 4 hours ago • 12 applicants</Text>
          </View>
        </View>

        {/* Tabs */}
        <View style={styles.tabRow}>
          {TABS.map((tab) => (
            <Pressable
              key={tab}
              style={[styles.tab, activeTab === tab && styles.tabActive]}
              onPress={() => setActiveTab(tab)}
            >
              <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>{tab}</Text>
            </Pressable>
          ))}
        </View>

        {/* Content */}
        {activeTab === 'Overview' && (
          <>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>About the Role</Text>
              <Text style={styles.bodyText}>
                As a Lead AI Solutions Architect, you will be at the forefront of bridging complex machine
                learning capabilities with real-world enterprise needs. You'll spearhead the design of
                scalable AI infrastructures and lead a team of high-performing engineers to deliver
                state-of-the-art LLM implementations for our Fortune 500 clients.
              </Text>
            </View>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Key Responsibilities</Text>
              {[
                'Design and implement scalable AI/ML pipelines',
                'Lead a team of 5-8 ML engineers',
                'Collaborate with product and business teams',
                'Ensure security and compliance of AI systems',
                'Evaluate and integrate emerging AI technologies',
              ].map((item, index) => (
                <View key={index} style={styles.listItem}>
                  <View style={styles.listDot} />
                  <Text style={styles.listText}>{item}</Text>
                </View>
              ))}
            </View>
          </>
        )}

        {activeTab === 'Requirements' && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Requirements</Text>
            {[
              '5+ years experience in ML/AI engineering',
              'Strong background in distributed systems',
              'Experience with PyTorch, TensorFlow, or JAX',
              'Knowledge of cloud platforms (AWS, GCP, Azure)',
              'PhD or MSc in Computer Science (preferred)',
              'Excellent communication and leadership skills',
            ].map((item, index) => (
              <View key={index} style={styles.listItem}>
                <Ionicons name="checkmark-circle" size={16} color={Colors.success} />
                <Text style={styles.listText}>{item}</Text>
              </View>
            ))}
          </View>
        )}

        {activeTab === 'Company' && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>About NeuralStream AI</Text>
            <Text style={styles.bodyText}>
              NeuralStream AI is a leading AI infrastructure company based in Palo Alto, California.
              Founded in 2020, we build enterprise-grade AI solutions for Fortune 500 companies.
              Our team of 200+ engineers and researchers pushes the boundaries of what's possible
              with large language models and generative AI.
            </Text>
            <View style={styles.companyStats}>
              <View style={styles.companyStat}>
                <Text style={styles.companyStatNumber}>200+</Text>
                <Text style={styles.companyStatLabel}>Employees</Text>
              </View>
              <View style={styles.companyStat}>
                <Text style={styles.companyStatNumber}>2020</Text>
                <Text style={styles.companyStatLabel}>Founded</Text>
              </View>
              <View style={styles.companyStat}>
                <Text style={styles.companyStatNumber}>$50M+</Text>
                <Text style={styles.companyStatLabel}>Funding</Text>
              </View>
            </View>
          </View>
        )}
      </ScrollView>

      {/* Bottom actions */}
      <View style={styles.bottomActions}>
        <Pressable style={styles.atsButton}>
          <Ionicons name="document-text" size={20} color={Colors.textWhite} />
          <Text style={styles.atsButtonText}>Pass to ATS Analysis</Text>
        </Pressable>
        <Pressable style={styles.interviewButton}>
          <Ionicons name="chatbubbles" size={20} color={Colors.primary} />
          <Text style={styles.interviewButtonText}>Start AI Interview</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { paddingTop: 56, paddingHorizontal: Spacing.xxl, paddingBottom: 180 },

  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    marginBottom: Spacing.xxl,
  },
  backButton: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { fontSize: FontSize.xl, fontWeight: FontWeight.bold, color: Colors.textPrimary },

  companyCard: { alignItems: 'center', marginBottom: Spacing.xxl },
  companyLogo: {
    width: 64, height: 64, borderRadius: BorderRadius.lg, backgroundColor: Colors.primary,
    justifyContent: 'center', alignItems: 'center', marginBottom: Spacing.lg,
  },
  jobTitle: { fontSize: FontSize.xxxl, fontWeight: FontWeight.bold, color: Colors.textPrimary, textAlign: 'center', marginBottom: Spacing.md },
  companyMeta: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: 4 },
  companyText: { fontSize: FontSize.sm, color: Colors.textSecondary },

  tabRow: {
    flexDirection: 'row', borderBottomWidth: 1, borderBottomColor: Colors.border,
    marginBottom: Spacing.xxl,
  },
  tab: { flex: 1, paddingVertical: Spacing.md, alignItems: 'center', borderBottomWidth: 2, borderBottomColor: 'transparent' },
  tabActive: { borderBottomColor: Colors.primary },
  tabText: { fontSize: FontSize.md, fontWeight: FontWeight.medium, color: Colors.textSecondary },
  tabTextActive: { color: Colors.primary, fontWeight: FontWeight.semibold },

  section: { marginBottom: Spacing.xxl },
  sectionTitle: { fontSize: FontSize.xl, fontWeight: FontWeight.bold, color: Colors.textPrimary, marginBottom: Spacing.lg },
  bodyText: { fontSize: FontSize.md, color: Colors.textSecondary, lineHeight: 24 },

  listItem: { flexDirection: 'row', alignItems: 'flex-start', gap: Spacing.md, marginBottom: Spacing.md },
  listDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: Colors.primary, marginTop: 7 },
  listText: { flex: 1, fontSize: FontSize.md, color: Colors.textSecondary, lineHeight: 22 },

  companyStats: { flexDirection: 'row', gap: Spacing.md, marginTop: Spacing.xxl },
  companyStat: {
    flex: 1, backgroundColor: Colors.backgroundSecondary, borderRadius: BorderRadius.md,
    padding: Spacing.lg, alignItems: 'center', gap: 4,
  },
  companyStatNumber: { fontSize: FontSize.xxl, fontWeight: FontWeight.extrabold, color: Colors.primary },
  companyStatLabel: { fontSize: FontSize.xs, color: Colors.textSecondary },

  bottomActions: {
    position: 'absolute', bottom: 0, left: 0, right: 0,
    backgroundColor: Colors.background, borderTopWidth: 1, borderTopColor: Colors.border,
    padding: Spacing.xxl, gap: Spacing.md, paddingBottom: 36,
  },
  atsButton: {
    backgroundColor: Colors.primary, borderRadius: BorderRadius.xl, paddingVertical: Spacing.lg,
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: Spacing.sm,
  },
  atsButtonText: { color: Colors.textWhite, fontSize: FontSize.lg, fontWeight: FontWeight.semibold },
  interviewButton: {
    borderWidth: 1.5, borderColor: Colors.primary, borderRadius: BorderRadius.xl, paddingVertical: Spacing.lg,
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: Spacing.sm,
  },
  interviewButtonText: { color: Colors.primary, fontSize: FontSize.lg, fontWeight: FontWeight.semibold },
});
