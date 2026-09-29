package com.oathbound.client;

import com.oathbound.Config;
import com.oathbound.Oathbound;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.BackupConfirmScreen;
import net.minecraft.client.gui.screens.ConfirmScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.event.TickEvent;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;

/**
 * Oathbound's dimension and structures are data-pack world generation, which vanilla labels "experimental".
 * That costs players two confirmation prompts (on world creation and on loading a world for the first time).
 * When {@code skipExperimentalWarning} is on, this presses "proceed" on exactly those two prompts (without a
 * backup, as the button itself would). Every other confirm screen is left alone.
 */
public final class PromptAnswerer {
    private static Screen waiting;

    private PromptAnswerer() {}

    private static boolean titled(Screen s, String key) {
        return s.getTitle().getString().equals(Component.translatable(key).getString());
    }

    static void onScreenOpening(ScreenEvent.Opening event) {
        if (!Config.skipExperimentalWarning()) return;
        Screen s = event.getNewScreen();
        if ((s instanceof BackupConfirmScreen && titled(s, "selectWorld.backupQuestion.experimental"))
            || (s instanceof ConfirmScreen && titled(s, "selectWorld.warning.experimental.title"))) {
            waiting = s;
        }
    }

    static void onClientTick(TickEvent.ClientTickEvent.Post event) {
        Screen s = waiting;
        if (s == null) return;
        waiting = null;
        if (Minecraft.getInstance().screen != s) return;
        boolean done = s instanceof BackupConfirmScreen ? pressProceed(s, BackupConfirmScreen.class, false) : pressProceed(s, ConfirmScreen.class, true);
        Oathbound.LOGGER.info(done ? "Answered the experimental-settings prompt ({})" : "Could not answer the experimental-settings prompt ({})",
            s.getClass().getSimpleName());
    }

    /**
     * Finds the screen's callback (a functional-interface field) and invokes its single method with booleans:
     * {@code value} for a yes/no consumer, false for "make a backup" style flags.
     */
    private static boolean pressProceed(Screen screen, Class<?> owner, boolean value) {
        for (Field f : owner.getDeclaredFields()) {
            if (Modifier.isStatic(f.getModifiers()) || !f.getType().isInterface()) continue;
            try {
                f.setAccessible(true);
                Object callback = f.get(screen);
                if (callback == null) continue;
                for (Method m : f.getType().getMethods()) {
                    if (!Modifier.isAbstract(m.getModifiers())) continue;
                    Class<?>[] params = m.getParameterTypes();
                    boolean allBool = params.length > 0;
                    for (Class<?> p : params) allBool &= p == boolean.class;
                    if (!allBool) continue;
                    Object[] args = new Object[params.length];
                    for (int i = 0; i < args.length; i++) args[i] = params.length == 1 ? value : Boolean.FALSE;
                    m.setAccessible(true);
                    m.invoke(callback, args);
                    return true;
                }
            } catch (ReflectiveOperationException | RuntimeException e) {
                Oathbound.LOGGER.debug("prompt field {} not usable", f.getName(), e);
            }
        }
        return false;
    }
}
