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
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, FontWeight, Spacing, BorderRadius } from '../../src/constants/theme';

interface ChatMessage {
  id: string;
  role: 'ai' | 'user';
  content: string;
  suggestions?: string[];
}

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: '1',
    role: 'ai',
    content:
      "Hi! 👋 I'm Nexora, your AI career assistant. I'm here to help you with job search, CV improvement, salary negotiation, and career coaching. How can I help you today?",
    suggestions: [
      'Analyze my CV',
      'Recommend jobs for me',
      'Help with cover letter',
      'Salary advice',
    ],
  },
];

export default function ChatbotScreen() {
  const router = useRouter();
  const flatListRef = useRef<FlatList>(null);
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [inputText, setInputText] = useState('');

  const handleSend = (text?: string) => {
    const msg = text || inputText.trim();
    if (!msg) return;

    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', content: msg };
    setMessages((prev) => [...prev, userMsg]);
    setInputText('');

    // Simulate AI response
    setTimeout(() => {
      let aiContent = '';
      let suggestions: string[] = [];

      if (msg.toLowerCase().includes('cv') || msg.toLowerCase().includes('resume')) {
        aiContent =
          "I'd be happy to analyze your CV! 📄 You can upload your CV in the ATS Analysis section for a detailed breakdown of your score, strengths, and areas for improvement. Would you like me to take you there?";
        suggestions = ['Go to ATS Analysis', 'Tips for a good CV', 'What is ATS?'];
      } else if (msg.toLowerCase().includes('job') || msg.toLowerCase().includes('recommend')) {
        aiContent =
          "Based on your profile, I recommend looking at roles in AI/ML Engineering, Full-Stack Development, and Data Science. These align with your technical skills. Here are some tips:\n\n• Focus on companies with remote-first cultures\n• Target roles matching 70%+ of your skills\n• Apply within the first 48 hours of posting";
        suggestions = ['Show me jobs', 'Improve my profile', 'Set up job alerts'];
      } else if (msg.toLowerCase().includes('salary') || msg.toLowerCase().includes('salaire')) {
        aiContent =
          "For your experience level and location, here's what the market looks like:\n\n💰 Junior: $60K - $85K\n💰 Mid-level: $90K - $130K\n💰 Senior: $140K - $200K\n\nThese are based on current market data for tech roles. Want a more precise estimate?";
        suggestions = ['Negotiation tips', 'Salary by location', 'Benefits to ask for'];
      } else if (msg.toLowerCase().includes('cover') || msg.toLowerCase().includes('lettre')) {
        aiContent =
          "I can help you write a compelling cover letter! 📝 To create a personalized letter, I'll need:\n\n1. The job title you're applying for\n2. The company name\n3. Your key strengths\n\nOr I can generate one based on your CV and a job posting. Want to try it?";
        suggestions = ['Generate cover letter', 'Cover letter tips', 'See templates'];
      } else {
        aiContent =
          "That's an interesting question! Let me help you with that. Could you provide more details so I can give you the most relevant advice?";
        suggestions = ['Help with CV', 'Job recommendations', 'Interview practice', 'Salary info'];
      }

      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: aiContent,
        suggestions,
      };
      setMessages((prev) => [...prev, aiMsg]);
    }, 1200);
  };

  const renderMessage = ({ item }: { item: ChatMessage }) => (
    <View style={styles.messageContainer}>
      <View
        style={[styles.messageBubble, item.role === 'user' ? styles.userBubble : styles.aiBubble]}
      >
        {item.role === 'ai' && (
          <View style={styles.aiHeader}>
            <View style={styles.aiAvatar}>
              <Ionicons name="sparkles" size={14} color={Colors.textWhite} />
            </View>
            <Text style={styles.aiName}>Nexora AI</Text>
          </View>
        )}
        <Text style={[styles.messageText, item.role === 'user' ? styles.userText : styles.aiMsgText]}>
          {item.content}
        </Text>
      </View>
      {item.suggestions && (
        <View style={styles.suggestionsRow}>
          {item.suggestions.map((s, i) => (
            <Pressable key={i} style={styles.suggestionChip} onPress={() => handleSend(s)}>
              <Text style={styles.suggestionText}>{s}</Text>
            </Pressable>
          ))}
        </View>
      )}
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
        </Pressable>
        <View style={styles.headerCenter}>
          <View style={styles.headerAvatar}>
            <Ionicons name="sparkles" size={16} color={Colors.textWhite} />
          </View>
          <View>
            <Text style={styles.headerTitle}>Nexora AI Assistant</Text>
            <Text style={styles.headerSubtitle}>Always available</Text>
          </View>
        </View>
        <Pressable>
          <Ionicons name="ellipsis-vertical" size={20} color={Colors.textSecondary} />
        </Pressable>
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
        <TextInput
          style={styles.input}
          placeholder="Ask me anything..."
          placeholderTextColor={Colors.textTertiary}
          value={inputText}
          onChangeText={setInputText}
          multiline
        />
        <Pressable
          style={[styles.sendBtn, inputText.trim() ? styles.sendBtnActive : null]}
          onPress={() => handleSend()}
          disabled={!inputText.trim()}
        >
          <Ionicons name="send" size={20} color={inputText.trim() ? Colors.textWhite : Colors.textTertiary} />
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },

  header: {
    flexDirection: 'row', alignItems: 'center', paddingHorizontal: Spacing.lg,
    paddingTop: 52, paddingBottom: Spacing.md, gap: Spacing.md,
    borderBottomWidth: 1, borderBottomColor: Colors.borderLight,
  },
  backBtn: { width: 36, height: 36, justifyContent: 'center', alignItems: 'center' },
  headerCenter: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  headerAvatar: {
    width: 36, height: 36, borderRadius: 18, backgroundColor: Colors.accent,
    justifyContent: 'center', alignItems: 'center',
  },
  headerTitle: { fontSize: FontSize.lg, fontWeight: FontWeight.bold, color: Colors.textPrimary },
  headerSubtitle: { fontSize: FontSize.xs, color: Colors.success, fontWeight: FontWeight.medium },

  messagesList: { paddingHorizontal: Spacing.lg, paddingVertical: Spacing.lg, gap: Spacing.lg },

  messageContainer: { gap: Spacing.md },
  messageBubble: { maxWidth: '85%', borderRadius: BorderRadius.lg, padding: Spacing.lg },
  aiBubble: { alignSelf: 'flex-start', backgroundColor: Colors.backgroundSecondary, borderBottomLeftRadius: 4 },
  userBubble: { alignSelf: 'flex-end', backgroundColor: Colors.primary, borderBottomRightRadius: 4 },
  aiHeader: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.sm },
  aiAvatar: {
    width: 22, height: 22, borderRadius: 11, backgroundColor: Colors.accent,
    justifyContent: 'center', alignItems: 'center',
  },
  aiName: { fontSize: FontSize.xs, fontWeight: FontWeight.bold, color: Colors.accent },
  messageText: { fontSize: FontSize.md, lineHeight: 22 },
  aiMsgText: { color: Colors.textPrimary },
  userText: { color: Colors.textWhite },

  suggestionsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm, paddingLeft: Spacing.xs },
  suggestionChip: {
    borderWidth: 1, borderColor: Colors.accent, borderRadius: BorderRadius.full,
    paddingHorizontal: Spacing.lg, paddingVertical: Spacing.sm,
  },
  suggestionText: { fontSize: FontSize.sm, color: Colors.accent, fontWeight: FontWeight.medium },

  inputBar: {
    flexDirection: 'row', alignItems: 'flex-end', paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md, borderTopWidth: 1, borderTopColor: Colors.borderLight,
    gap: Spacing.sm, paddingBottom: 28,
  },
  input: {
    flex: 1, fontSize: FontSize.md, color: Colors.textPrimary, borderWidth: 1,
    borderColor: Colors.border, borderRadius: BorderRadius.xl, paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md, maxHeight: 100,
  },
  sendBtn: {
    width: 40, height: 40, borderRadius: 20, backgroundColor: Colors.backgroundTertiary,
    justifyContent: 'center', alignItems: 'center',
  },
  sendBtnActive: { backgroundColor: Colors.accent },
});
