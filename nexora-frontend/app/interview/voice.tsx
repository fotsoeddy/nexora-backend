import React, { useState } from 'react';
import {
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, FontWeight, Spacing, BorderRadius } from '../../src/constants/theme';

export default function VoiceInterviewScreen() {
  const router = useRouter();
  const [isMuted, setIsMuted] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);
  const [progress] = useState(20);
  const questionNum = 2;
  const totalQuestions = 10;

  const handleEnd = () => {
    router.push('/interview/result');
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textWhite} />
        </Pressable>
        <Text style={styles.headerTitle}>AI Voice Interview</Text>
        <Text style={styles.questionBadge}>Q{questionNum}/{totalQuestions}</Text>
      </View>

      {/* Progress */}
      <View style={styles.progressBar}>
        <View style={[styles.progressFill, { width: `${progress}%` }]} />
      </View>
      <Text style={styles.progressText}>{progress}% completed</Text>

      {/* Main content */}
      <View style={styles.mainContent}>
        {/* AI Avatar */}
        <View style={styles.avatarSection}>
          <View style={styles.avatarRing}>
            <View style={styles.avatar}>
              <Ionicons name="person" size={40} color={Colors.textWhite} />
            </View>
          </View>
          <Text style={styles.recruiterName}>Elite AI Recruiter</Text>
          <Text style={styles.speakingStatus}>AI Assistant is speaking...</Text>
        </View>

        {/* Audio Visualizer */}
        <View style={styles.visualizer}>
          {Array(24).fill(null).map((_, i) => {
            const height = Math.random() * 40 + 10;
            return (
              <View
                key={i}
                style={[
                  styles.visualizerBar,
                  { height, backgroundColor: i % 3 === 0 ? Colors.accent : Colors.accent + '60' },
                ]}
              />
            );
          })}
        </View>

        {/* Current question */}
        <View style={styles.questionCard}>
          <Text style={styles.questionLabel}>CURRENT QUESTION</Text>
          <Text style={styles.questionText}>
            "Can you describe your approach to designing scalable systems that handle millions of concurrent users?"
          </Text>
        </View>
      </View>

      {/* Controls */}
      <View style={styles.controls}>
        <Pressable
          style={[styles.controlBtn, isMuted && styles.controlBtnActive]}
          onPress={() => setIsMuted(!isMuted)}
        >
          <Ionicons name={isMuted ? 'mic-off' : 'mic'} size={24} color={isMuted ? Colors.textWhite : Colors.textPrimary} />
          <Text style={[styles.controlLabel, isMuted && styles.controlLabelActive]}>
            {isMuted ? 'Muted' : 'Mute'}
          </Text>
        </Pressable>

        <Pressable style={styles.endBtn} onPress={handleEnd}>
          <Ionicons name="close" size={28} color={Colors.textWhite} />
          <Text style={styles.endLabel}>End</Text>
        </Pressable>

        <Pressable
          style={[styles.controlBtn, isSpeakerOn && styles.controlBtnActive]}
          onPress={() => setIsSpeakerOn(!isSpeakerOn)}
        >
          <Ionicons name={isSpeakerOn ? 'volume-high' : 'volume-mute'} size={24} color={isSpeakerOn ? Colors.textWhite : Colors.textPrimary} />
          <Text style={[styles.controlLabel, isSpeakerOn && styles.controlLabelActive]}>Speaker</Text>
        </Pressable>
      </View>

      {/* Timer */}
      <Text style={styles.timer}>04:32</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.primary },

  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: Spacing.xxl, paddingTop: 52, paddingBottom: Spacing.md,
  },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { fontSize: FontSize.xl, fontWeight: FontWeight.bold, color: Colors.textWhite },
  questionBadge: {
    backgroundColor: 'rgba(255,255,255,0.15)', borderRadius: BorderRadius.full,
    paddingHorizontal: Spacing.md, paddingVertical: 4, fontSize: FontSize.sm,
    fontWeight: FontWeight.bold, color: Colors.textWhite, overflow: 'hidden',
  },

  progressBar: {
    height: 4, backgroundColor: 'rgba(255,255,255,0.15)', marginHorizontal: Spacing.xxl,
    borderRadius: 2, marginTop: Spacing.sm,
  },
  progressFill: { height: 4, backgroundColor: Colors.accent, borderRadius: 2 },
  progressText: {
    fontSize: FontSize.xs, color: 'rgba(255,255,255,0.5)', textAlign: 'center',
    marginTop: Spacing.sm,
  },

  mainContent: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: Spacing.xxxl },

  avatarSection: { alignItems: 'center', gap: Spacing.md },
  avatarRing: {
    width: 110, height: 110, borderRadius: 55, borderWidth: 3,
    borderColor: Colors.accent + '50', justifyContent: 'center', alignItems: 'center',
  },
  avatar: {
    width: 88, height: 88, borderRadius: 44, backgroundColor: Colors.accent,
    justifyContent: 'center', alignItems: 'center',
  },
  recruiterName: { fontSize: FontSize.xxl, fontWeight: FontWeight.bold, color: Colors.textWhite },
  speakingStatus: { fontSize: FontSize.md, color: 'rgba(255,255,255,0.6)' },

  visualizer: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    height: 60, gap: 3, paddingHorizontal: Spacing.xxl,
  },
  visualizerBar: { width: 4, borderRadius: 2 },

  questionCard: {
    marginHorizontal: Spacing.xxl, backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: BorderRadius.lg, padding: Spacing.xl, borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  questionLabel: {
    fontSize: FontSize.xs, fontWeight: FontWeight.bold, color: Colors.accent,
    letterSpacing: 1, marginBottom: Spacing.sm,
  },
  questionText: { fontSize: FontSize.md, color: Colors.textWhite, lineHeight: 22, fontStyle: 'italic' },

  controls: {
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center',
    gap: Spacing.xxxl, paddingVertical: Spacing.xxl,
  },
  controlBtn: {
    width: 56, height: 56, borderRadius: 28, backgroundColor: 'rgba(255,255,255,0.12)',
    justifyContent: 'center', alignItems: 'center',
  },
  controlBtnActive: { backgroundColor: Colors.accent },
  controlLabel: {
    fontSize: FontSize.xs, color: 'rgba(255,255,255,0.6)', marginTop: 4,
    position: 'absolute', bottom: -18, width: 60, textAlign: 'center',
  },
  controlLabelActive: { color: Colors.textWhite },
  endBtn: {
    width: 68, height: 68, borderRadius: 34, backgroundColor: Colors.error,
    justifyContent: 'center', alignItems: 'center',
  },
  endLabel: {
    fontSize: FontSize.xs, color: Colors.textWhite, fontWeight: FontWeight.bold,
    position: 'absolute', bottom: -18,
  },

  timer: {
    fontSize: FontSize.md, color: 'rgba(255,255,255,0.4)', textAlign: 'center',
    paddingBottom: 36, fontWeight: FontWeight.medium,
  },
});
