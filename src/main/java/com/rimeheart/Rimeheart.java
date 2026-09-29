package com.rimeheart;

import com.rimeheart.command.RimeheartCommand;
import com.rimeheart.entity.boss.FrostSovereignEntity;
import com.rimeheart.entity.boss.SovereignRitual;
import com.rimeheart.entity.mob.FrostWraithEntity;
import com.rimeheart.entity.mob.ShardlingEntity;
import com.rimeheart.frost.Frost;
import com.rimeheart.quest.QuestLog;
import com.rimeheart.registry.*;
import com.mojang.logging.LogUtils;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.loading.FMLEnvironment;
import org.slf4j.Logger;

/**
 * Rimeheart: the Long Winter. Frostiron and rime crystal, chill-based combat, Frost Wraiths, Shardlings,
 * the buried Frozen Sanctum and the Frost Sovereign, guided by the Warden's Journal quest book.
 */
@Mod(Rimeheart.MODID)
public final class Rimeheart {
    public static final String MODID = "rimeheart";
    public static final Logger LOGGER = LogUtils.getLogger();

    public Rimeheart(FMLJavaModLoadingContext context) {
        var modBus = context.getModBusGroup();
        ModBlocks.BLOCKS.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModEntities.ENTITIES.register(modBus);
        ModSounds.SOUNDS.register(modBus);
        ModParticles.PARTICLES.register(modBus);
        ModWorldgen.STRUCTURE_TYPES.register(modBus);
        ModWorldgen.STRUCTURE_PIECES.register(modBus);
        ModTabs.TABS.register(modBus);

        context.registerConfig(ModConfig.Type.COMMON, Config.SPEC);

        EntityAttributeCreationEvent.BUS.addListener(Rimeheart::attributes);
        SpawnPlacementRegisterEvent.BUS.addListener(Rimeheart::spawnPlacements);
        RegisterCommandsEvent.BUS.addListener(e -> RimeheartCommand.register(e.getDispatcher()));
        RegisterCommandsEvent.BUS.addListener(e -> QuestLog.register(e.getDispatcher()));
        TickEvent.LevelTickEvent.Post.BUS.addListener(Rimeheart::levelTick);
        TickEvent.PlayerTickEvent.Post.BUS.addListener(e -> Frost.onPlayerTick(e.player()));
        ServerStartedEvent.BUS.addListener(SelfTest::onServerStarted);
        TickEvent.ServerTickEvent.Post.BUS.addListener(SelfTest::onServerTick);

        if (FMLEnvironment.dist == Dist.CLIENT) {
            com.rimeheart.client.ClientSetup.init(context);
        }
    }

    private static void attributes(EntityAttributeCreationEvent event) {
        event.put(ModEntities.FROST_WRAITH.get(), FrostWraithEntity.createAttributes().build());
        event.put(ModEntities.SHARDLING.get(), ShardlingEntity.createAttributes().build());
        event.put(ModEntities.FROST_SOVEREIGN.get(), FrostSovereignEntity.createAttributes().build());
    }

    private static void spawnPlacements(SpawnPlacementRegisterEvent event) {
        event.register(ModEntities.FROST_WRAITH.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
            Monster::checkMonsterSpawnRules, SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(ModEntities.SHARDLING.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
            Monster::checkMonsterSpawnRules, SpawnPlacementRegisterEvent.Operation.REPLACE);
    }

    private static void levelTick(TickEvent.LevelTickEvent.Post event) {
        if (event.level() instanceof ServerLevel level) {
            SovereignRitual.tick(level);
        }
    }
}
