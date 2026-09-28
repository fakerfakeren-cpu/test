package com.astralfall.client;

import com.astralfall.Astralfall;
import com.astralfall.Config;
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
 * Astralfall's structures and impact sites are data-pack world generation, which vanilla flags as
 * "experimental": every world load asks "Worlds using Experimental Settings are not supported" and world
 * creation shows an experimental-settings warning. This answers those two prompts the way a player
 * clicking "I Know What I'm Doing!" / "Proceed" would, one tick after they open. Other prompts are untouched.
 */
public final class ExperimentalWarningSkipper {
    private static Screen pending;

    private ExperimentalWarningSkipper() {}

    static void onScreenOpening(ScreenEvent.Opening event) {
        if (!Config.skipExperimentalWarning()) return;
        Screen screen = event.getNewScreen();
        if (screen == null) return;
        String title = screen.getTitle().getString();
        if (screen instanceof BackupConfirmScreen && title.equals(Component.translatable("selectWorld.backupQuestion.experimental").getString())) {
            pending = screen;
        } else if (screen instanceof ConfirmScreen && title.equals(Component.translatable("selectWorld.warning.experimental.title").getString())) {
            pending = screen;
        }
    }

    static void onClientTick(TickEvent.ClientTickEvent.Post event) {
        Screen screen = pending;
        if (screen == null) return;
        pending = null;
        try {
            if (screen instanceof BackupConfirmScreen) {
                Field field = BackupConfirmScreen.class.getDeclaredField("onProceed");
                field.setAccessible(true);
                Object listener = field.get(screen);
                // Listener.proceed(boolean backup, boolean eraseCache)
                if (invoke(listener, field.getType(), false, false)) {
                    Astralfall.LOGGER.info("Skipped the 'Experimental Settings' world-load prompt (config: skipExperimentalWarning)");
                }
            } else {
                for (Field field : ConfirmScreen.class.getDeclaredFields()) {
                    if (field.getType().getName().endsWith("BooleanConsumer")) {
                        field.setAccessible(true);
                        if (invoke(field.get(screen), field.getType(), true)) {
                            Astralfall.LOGGER.info("Skipped the experimental world-creation warning (config: skipExperimentalWarning)");
                        }
                        return;
                    }
                }
            }
        } catch (Throwable t) {
            Astralfall.LOGGER.warn("Could not skip the experimental-settings prompt; click 'I Know What I'm Doing!' instead", t);
        }
    }

    /** Calls the single abstract method of a functional interface whose parameters are all booleans. */
    private static boolean invoke(Object target, Class<?> type, Object... args) throws Exception {
        for (Method m : type.getMethods()) {
            if (!Modifier.isAbstract(m.getModifiers()) || m.getParameterCount() != args.length) continue;
            boolean allBool = true;
            for (Class<?> p : m.getParameterTypes()) allBool &= p == boolean.class;
            if (!allBool) continue;
            m.setAccessible(true);
            m.invoke(target, args);
            return true;
        }
        return false;
    }
}
