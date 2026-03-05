import React, { useState } from 'react';
import {
  FlatList,
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

const FILTERS = [
  { id: 'location', label: 'Location', icon: 'location' as const },
  { id: 'type', label: 'Type', icon: 'briefcase' as const },
  { id: 'level', label: 'Level', icon: 'bar-chart' as const },
];

const JOBS = [
  {
    id: '1',
    title: 'Lead ML Engineer',
    company: 'NeuralFlow',
    location: 'San Francisco',
    tags: ['PYTHON', 'PYTORCH', '$180K-$240K'],
    postedAgo: '2+ ago',
    iconBg: '#3B82F6',
    icon: 'hardware-chip' as const,
  },
  {
    id: '2',
    title: 'AI Product Designer',
    company: 'Synthesis',
    location: 'London / Remote',
    tags: ['FIGMA', 'LLMux', 'HYBRID'],
    postedAgo: '5+ ago',
    iconBg: '#8B5CF6',
    icon: 'color-palette' as const,
  },
  {
    id: '3',
    title: 'Senior NLP Scientist',
    company: 'CognitCore',
    location: 'New York',
    tags: ['TRANSFORMERS', 'PhD REQUIRED', 'FULL-TIME'],
    postedAgo: 'Yesterday',
    iconBg: '#10B981',
    icon: 'flask' as const,
  },
  {
    id: '4',
    title: 'Data Engineer',
    company: 'DataPipeline Inc',
    location: 'Douala / Remote',
    tags: ['SPARK', 'AWS', 'SQL'],
    postedAgo: '3 days ago',
    iconBg: '#F59E0B',
    icon: 'server' as const,
  },
  {
    id: '5',
    title: 'Frontend Developer',
    company: 'INSAM Technologies',
    location: 'Yaoundé',
    tags: ['REACT', 'TYPESCRIPT', 'MOBILE'],
    postedAgo: '1 day ago',
    iconBg: '#EC4899',
    icon: 'code-slash' as const,
  },
];

export default function JobsScreen() {
  const router = useRouter();
  const [searchText, setSearchText] = useState('');

  const renderJob = ({ item }: { item: typeof JOBS[0] }) => (
    <Pressable
      style={styles.jobCard}
      onPress={() => router.push(`/job/${item.id}`)}
    >
      <View style={styles.jobCardHeader}>
        <View style={[styles.jobIcon, { backgroundColor: item.iconBg }]}>
          <Ionicons name={item.icon} size={20} color={Colors.textWhite} />
        </View>
        <View style={styles.jobInfo}>
          <Text style={styles.jobTitle}>{item.title}</Text>
          <Text style={styles.jobCompany}>
            {item.company} • {item.location}
          </Text>
        </View>
        <Pressable style={styles.bookmarkButton}>
          <Ionicons name="bookmark-outline" size={20} color={Colors.textSecondary} />
        </Pressable>
      </View>
      <View style={styles.tagsRow}>
        {item.tags.map((tag, index) => (
          <View key={index} style={styles.tag}>
            <Text style={styles.tagText}>{tag}</Text>
          </View>
        ))}
      </View>
      <View style={styles.jobFooter}>
        <Text style={styles.postedText}>Posted {item.postedAgo}</Text>
        <Pressable
          style={styles.viewButton}
          onPress={() => router.push(`/job/${item.id}`)}
        >
          <Text style={styles.viewButtonText}>View</Text>
        </Pressable>
      </View>
    </Pressable>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <View style={styles.logoIcon}>
            <Ionicons name="flash" size={18} color={Colors.textWhite} />
          </View>
          <Text style={styles.headerTitle}>AI Careers</Text>
        </View>
        <Pressable>
          <Ionicons name="person-circle-outline" size={28} color={Colors.textSecondary} />
        </Pressable>
      </View>

      {/* Search */}
      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color={Colors.textTertiary} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search roles, companies..."
          placeholderTextColor={Colors.textTertiary}
          value={searchText}
          onChangeText={setSearchText}
        />
      </View>

      {/* Filters */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.filtersContainer}
      >
        {FILTERS.map((filter) => (
          <Pressable key={filter.id} style={styles.filterChip}>
            <Ionicons name={filter.icon} size={16} color={Colors.textSecondary} />
            <Text style={styles.filterText}>{filter.label}</Text>
            <Ionicons name="chevron-down" size={14} color={Colors.textSecondary} />
          </Pressable>
        ))}
      </ScrollView>

      {/* Results */}
      <View style={styles.resultsHeader}>
        <Text style={styles.resultsLabel}>FEATURED ROLES</Text>
        <Text style={styles.resultsCount}>{JOBS.length} results</Text>
      </View>

      {/* Job list */}
      <FlatList
        data={JOBS}
        renderItem={renderJob}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
    paddingTop: 56,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.xxl,
    marginBottom: Spacing.lg,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
  },
  logoIcon: {
    width: 32,
    height: 32,
    borderRadius: BorderRadius.sm,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: FontSize.xxl,
    fontWeight: FontWeight.bold,
    color: Colors.textPrimary,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.backgroundSecondary,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.lg,
    height: 48,
    marginHorizontal: Spacing.xxl,
    marginBottom: Spacing.lg,
    gap: Spacing.md,
  },
  searchInput: {
    flex: 1,
    fontSize: FontSize.md,
    color: Colors.textPrimary,
  },
  filtersContainer: {
    paddingHorizontal: Spacing.xxl,
    gap: Spacing.md,
    marginBottom: Spacing.lg,
  },
  filterChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.full,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm + 2,
  },
  filterText: {
    fontSize: FontSize.sm,
    fontWeight: FontWeight.medium,
    color: Colors.textSecondary,
  },
  resultsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.xxl,
    marginBottom: Spacing.lg,
  },
  resultsLabel: {
    fontSize: FontSize.sm,
    fontWeight: FontWeight.semibold,
    color: Colors.textSecondary,
    letterSpacing: 0.5,
  },
  resultsCount: {
    fontSize: FontSize.sm,
    color: Colors.accent,
    fontWeight: FontWeight.medium,
  },
  listContent: {
    paddingHorizontal: Spacing.xxl,
    gap: Spacing.md,
    paddingBottom: 24,
  },
  jobCard: {
    backgroundColor: Colors.background,
    borderWidth: 1,
    borderColor: Colors.borderLight,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    gap: Spacing.md,
    ...Shadows.sm,
  },
  jobCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
  },
  jobIcon: {
    width: 44,
    height: 44,
    borderRadius: BorderRadius.md,
    justifyContent: 'center',
    alignItems: 'center',
  },
  jobInfo: {
    flex: 1,
    gap: 2,
  },
  jobTitle: {
    fontSize: FontSize.lg,
    fontWeight: FontWeight.bold,
    color: Colors.textPrimary,
  },
  jobCompany: {
    fontSize: FontSize.sm,
    color: Colors.textSecondary,
  },
  bookmarkButton: {
    padding: Spacing.xs,
  },
  tagsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.sm,
  },
  tag: {
    backgroundColor: Colors.backgroundTertiary,
    borderRadius: 6,
    paddingHorizontal: Spacing.md,
    paddingVertical: 4,
  },
  tagText: {
    fontSize: FontSize.xs,
    fontWeight: FontWeight.semibold,
    color: Colors.textSecondary,
  },
  jobFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  postedText: {
    fontSize: FontSize.sm,
    color: Colors.textTertiary,
  },
  viewButton: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.sm,
    paddingHorizontal: Spacing.xl,
    paddingVertical: Spacing.sm,
  },
  viewButtonText: {
    fontSize: FontSize.md,
    fontWeight: FontWeight.semibold,
    color: Colors.textWhite,
  },
});
