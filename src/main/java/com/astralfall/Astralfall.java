package com.astralfall;

import com.mojang.logging.LogUtils;
import net.minecraft.server.MinecraftServer;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;

@Mod(Astralfall.MODID)
public final class Astralfall {
    public static final String MODID = "astralfall";
    public static final Logger LOGGER = LogUtils.getLogger();

    public Astralfall(FMLJavaModLoadingContext context) {
        ServerStartedEvent.BUS.addListener(Astralfall::onServerStarted);
    }

    private static void onServerStarted(ServerStartedEvent event) {
        if (!Boolean.getBoolean("astralfall.selftest")) return;
        MinecraftServer server = event.getServer();
        LOGGER.info("[SELFTEST] Astralfall loaded on {}", server.getServerVersion());
        LOGGER.info("[SELFTEST] RESULT: PASS");
        server.halt(false);
    }
}
