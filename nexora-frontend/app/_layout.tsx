import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <>
      <StatusBar style="dark" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="onboarding" />
        <Stack.Screen name="(auth)" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen
          name="job/[id]"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="interview/[id]"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="interview/result"
          options={{ animation: 'slide_from_bottom' }}
        />
        <Stack.Screen
          name="interview/voice"
          options={{ animation: 'fade' }}
        />
        <Stack.Screen
          name="chat/index"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="cv/cover-letter"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="salary/index"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="alerts/index"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="applications/index"
          options={{ animation: 'slide_from_right' }}
        />
        <Stack.Screen
          name="saved/index"
          options={{ animation: 'slide_from_right' }}
        />
      </Stack>
    </>
  );
}
