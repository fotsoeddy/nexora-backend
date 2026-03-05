import React, { useRef, useState } from 'react';
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, FontWeight, Spacing, BorderRadius, Shadows } from '../../src/constants/theme';

interface Message {
  id: string;
  role: 'ai' | 'user';
  content: string;
  timestamp: string;
}

const INITIAL_MESSAGES: Message[] = [
  {
    id: '1',
    role: 'ai',
    content:
      "Hello! To start, could you tell me about a challenging technical project you've managed recently? Specifically, what was your role in the architecture?",
    timestamp: '14:01',
  },
  {
    id: '2',
    role: 'user',
    content:
      "Certainly. Last year, I led a team of four to migrate our legacy monolith to a microservices architecture using AWS and Kubernetes. I was responsible for the initial system design and the CI/CD pipeline implementation.",
    timestamp: '14:02',
  },
  {
    id: '3',
    role: 'ai',
    content:
      "That sounds significant. What was the biggest bottleneck you encountered during the migration phase, and how did you resolve it?",
    timestamp: '14:03',
  },
];

export default function InterviewChatScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams();
  const flatListRef = useRef<FlatList>(null);
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [inputText, setInputText] = useState('');
  const [progress] = useState(20);
  const [questionNum] = useState(2);
  const totalQuestions = 10;

  const handleSend = () => {
    if (!inputText.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputText.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputText('');

    // Simulate AI response
    setTimeout(() => {
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content:
          "Excellent answer. Now, can you walk me through how you handle conflict resolution within your engineering team? Give me a specific example.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, aiMsg]);
    }, 1500);
  };

  const renderMessage = ({ item }: { item: Message }) => (
    <View
      style={[
        styles.messageBubble,
        item.role === 'user' ? styles.userBubble : styles.aiBubble,
      ]}
    >
      {item.role === 'ai' && (
        <View style={styles.aiLabel}>
          <Ionicons name="sparkles" size={12} color={Colors.accent} />
          <Text style={styles.aiLabelText}>AI Assistant</Text>
        </View>
      )}
      <Text
        style={[
          styles.messageText,
          item.role === 'user' ? styles.userText : styles.aiText,
        ]}
      >
        {item.content}
      </Text>
      <Text style={[styles.timestamp, item.role === 'user' && styles.userTimestamp]}>
        {item.timestamp}
      </Text>
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={0}
    >
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
        </Pressable>
        <View style={styles.headerCenter}>
          <View style={styles.recruiterAvatar}>
            <Ionicons name="person" size={18} color={Colors.textWhite} />
          </View>
          <View>
            <Text style={styles.recruiterName}>Elite AI Recruiter</Text>
            <Text style={styles.recruiterStatus}>Active Now</Text>
          </View>
        </View>
        <Text style={styles.questionLabel}>Question {questionNum} of {totalQuestions}</Text>
      </View>

      {/* Progress bar */}
      <View style={styles.progressBar}>
        <View style={[styles.progressFill, { width: `${progress}%` }]} />
      </View>

      {/* Messages */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.messagesList}
        showsVerticalScrollIndicator={false}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {/* Input */}
      <View style={styles.inputBar}>
        <Pressable style={styles.attachBtn}>
          <Ionicons name="attach" size={22} color={Colors.textSecondary} />
        </Pressable>
        <TextInput
          style={styles.input}
          placeholder="Type your answer here..."
          placeholderTextColor={Colors.textTertiary}
          value={inputText}
          onChangeText={setInputText}
          multiline
        />
        <Pressable
          style={[styles.sendBtn, inputText.trim() ? styles.sendBtnActive : null]}
          onPress={handleSend}
          disabled={!inputText.trim()}
        >
          <Ionicons
            name="send"
            size={20}
            color={inputText.trim() ? Colors.textWhite : Colors.textTertiary}
          />
        </Pressable>
      </View>

      {/* Security label */}
      <View style={styles.securityBar}>
        <Ionicons name="lock-closed" size={12} color={Colors.textTertiary} />
        <Text style={styles.securityText}>SECURE AI INTERVIEW SESSION</Text>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },

  header: {
    flexDirection: 'row', alignItems: 'center', paddingHorizontal: Spacing.lg,
    paddingTop: 52, paddingBottom: Spacing.md, gap: Spacing.md,
    backgroundColor: Colors.background, borderBottomWidth: 1, borderBottomColor: Colors.borderLight,
  },
  backBtn: { width: 36, height: 36, justifyContent: 'center', alignItems: 'center' },
  headerCenter: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  recruiterAvatar: {
    width: 36, height: 36, borderRadius: 18, backgroundColor: Colors.primary,
    justifyContent: 'center', alignItems: 'center',
  },
  recruiterName: { fontSize: FontSize.md, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  recruiterStatus: { fontSize: FontSize.xs, color: Colors.success, fontWeight: FontWeight.medium },
  questionLabel: { fontSize: FontSize.xs, color: Colors.textSecondary, fontWeight: FontWeight.medium },

  progressBar: {
    height: 4, backgroundColor: Colors.backgroundTertiary, marginHorizontal: Spacing.xxl,
    borderRadius: 2, marginVertical: Spacing.sm,
  },
  progressFill: { height: 4, backgroundColor: Colors.accent, borderRadius: 2 },

  messagesList: { paddingHorizontal: Spacing.lg, paddingVertical: Spacing.lg, gap: Spacing.lg },

  messageBubble: { maxWidth: '82%', borderRadius: BorderRadius.lg, padding: Spacing.lg },
  aiBubble: {
    alignSelf: 'flex-start', backgroundColor: Colors.backgroundSecondary,
    borderBottomLeftRadius: 4,
  },
  userBubble: {
    alignSelf: 'flex-end', backgroundColor: Colors.primary,
    borderBottomRightRadius: 4,
  },
  aiLabel: { flexDirection: 'row', alignItems: 'center', gap: 4, marginBottom: Spacing.sm },
  aiLabelText: { fontSize: FontSize.xs, color: Colors.accent, fontWeight: FontWeight.semibold },
  messageText: { fontSize: FontSize.md, lineHeight: 22 },
  aiText: { color: Colors.textPrimary },
  userText: { color: Colors.textWhite },
  timestamp: { fontSize: FontSize.xs, color: Colors.textTertiary, marginTop: Spacing.sm, alignSelf: 'flex-end' },
  userTimestamp: { color: 'rgba(255,255,255,0.6)' },

  inputBar: {
    flexDirection: 'row', alignItems: 'flex-end', paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md, borderTopWidth: 1, borderTopColor: Colors.borderLight,
    gap: Spacing.sm, backgroundColor: Colors.background,
  },
  attachBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  input: {
    flex: 1, fontSize: FontSize.md, color: Colors.textPrimary, borderWidth: 1,
    borderColor: Colors.border, borderRadius: BorderRadius.xl, paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md, maxHeight: 100,
  },
  sendBtn: {
    width: 40, height: 40, borderRadius: 20, backgroundColor: Colors.backgroundTertiary,
    justifyContent: 'center', alignItems: 'center',
  },
  sendBtnActive: { backgroundColor: Colors.primary },

  securityBar: {
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center',
    gap: Spacing.xs, paddingBottom: 28, paddingTop: Spacing.sm,
  },
  securityText: { fontSize: 9, color: Colors.textTertiary, letterSpacing: 1, fontWeight: FontWeight.medium },
});
