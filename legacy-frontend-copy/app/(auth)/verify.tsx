import React, { useRef, useState } from 'react';
import {
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, FontWeight, Spacing, BorderRadius } from '../../src/constants/theme';

const CODE_LENGTH = 6;

export default function VerifyScreen() {
  const router = useRouter();
  const [code, setCode] = useState<string[]>(Array(CODE_LENGTH).fill(''));
  const inputs = useRef<(TextInput | null)[]>([]);

  const handleChange = (text: string, index: number) => {
    const newCode = [...code];
    newCode[index] = text;
    setCode(newCode);

    if (text && index < CODE_LENGTH - 1) {
      inputs.current[index + 1]?.focus();
    }
  };

  const handleKeyPress = (key: string, index: number) => {
    if (key === 'Backspace' && !code[index] && index > 0) {
      inputs.current[index - 1]?.focus();
    }
  };

  const handleVerify = () => {
    router.replace('/(tabs)');
  };

  return (
    <View style={styles.container}>
      {/* Icon */}
      <View style={styles.iconContainer}>
        <View style={styles.iconCircle}>
          <Ionicons name="mail" size={40} color={Colors.accent} />
        </View>
      </View>

      {/* Title */}
      <Text style={styles.title}>Verify your email</Text>
      <Text style={styles.subtitle}>
        We've sent a 6-digit verification code to{'\n'}
        <Text style={styles.email}>candidate@ai-recruitment.io</Text>
      </Text>

      {/* OTP Inputs */}
      <View style={styles.otpContainer}>
        {Array(CODE_LENGTH)
          .fill(null)
          .map((_, index) => (
            <TextInput
              key={index}
              ref={(ref) => (inputs.current[index] = ref)}
              style={[styles.otpInput, code[index] ? styles.otpInputFilled : null]}
              maxLength={1}
              keyboardType="number-pad"
              value={code[index]}
              onChangeText={(text) => handleChange(text, index)}
              onKeyPress={({ nativeEvent }) => handleKeyPress(nativeEvent.key, index)}
              selectionColor={Colors.accent}
            />
          ))}
      </View>

      {/* Verify Button */}
      <Pressable style={styles.primaryButton} onPress={handleVerify}>
        <Text style={styles.primaryButtonText}>Verify Account</Text>
        <Ionicons name="arrow-forward" size={20} color={Colors.textWhite} />
      </Pressable>

      {/* Resend */}
      <View style={styles.resendRow}>
        <Text style={styles.resendText}>Didn't receive the code? </Text>
        <Pressable>
          <Text style={styles.resendLink}>Resend Code</Text>
        </Pressable>
      </View>

      {/* Security note */}
      <View style={styles.securityRow}>
        <Ionicons name="lock-closed" size={14} color={Colors.textTertiary} />
        <Ionicons name="shield-checkmark" size={14} color={Colors.textTertiary} />
        <Text style={styles.securityText}>SECURE VERIFICATION SYSTEM</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
    paddingHorizontal: Spacing.xxl,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconContainer: {
    marginBottom: Spacing.xxxl,
  },
  iconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: Colors.accent + '15',
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: FontSize.xxxl,
    fontWeight: FontWeight.bold,
    color: Colors.textPrimary,
    marginBottom: Spacing.md,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: FontSize.md,
    color: Colors.textSecondary,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: Spacing.xxxl,
  },
  email: {
    color: Colors.accent,
    fontWeight: FontWeight.semibold,
  },
  otpContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: Spacing.md,
    marginBottom: Spacing.xxxl,
  },
  otpInput: {
    width: 48,
    height: 56,
    borderWidth: 1.5,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    textAlign: 'center',
    fontSize: FontSize.xxl,
    fontWeight: FontWeight.bold,
    color: Colors.textPrimary,
  },
  otpInputFilled: {
    borderColor: Colors.accent,
    backgroundColor: Colors.accent + '08',
  },
  primaryButton: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.xl,
    paddingVertical: Spacing.lg + 2,
    paddingHorizontal: Spacing.huge,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: Spacing.sm,
    width: '100%',
    marginBottom: Spacing.xxl,
  },
  primaryButtonText: {
    color: Colors.textWhite,
    fontSize: FontSize.xl,
    fontWeight: FontWeight.semibold,
  },
  resendRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.huge,
  },
  resendText: {
    fontSize: FontSize.md,
    color: Colors.textSecondary,
  },
  resendLink: {
    fontSize: FontSize.md,
    color: Colors.textPrimary,
    fontWeight: FontWeight.bold,
    textDecorationLine: 'underline',
  },
  securityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
  },
  securityText: {
    fontSize: FontSize.xs,
    color: Colors.textTertiary,
    letterSpacing: 1,
    fontWeight: FontWeight.medium,
  },
});
