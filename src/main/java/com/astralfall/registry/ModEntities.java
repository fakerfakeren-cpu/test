package com.astralfall.registry;

import com.astralfall.Astralfall;
import com.astralfall.entity.MeteorEntity;
import com.astralfall.entity.SingularityEntity;
import com.astralfall.entity.boss.AstraeusEntity;
import com.astralfall.entity.mob.AstralWispEntity;
import com.astralfall.entity.mob.MeteoriteCrawlerEntity;
import com.astralfall.entity.mob.VoidGazerEntity;
import com.astralfall.entity.mob.VoidStalkerEntity;
import com.astralfall.entity.projectile.CrystalShardEntity;
import com.astralfall.entity.projectile.SingularityGrenadeEntity;
import com.astralfall.entity.projectile.StarBoltEntity;
import com.astralfall.entity.projectile.StarSlashEntity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, Astralfall.MODID);

    public static final RegistryObject<EntityType<MeteorEntity>> METEOR = ENTITIES.register("meteor", () ->
        EntityType.Builder.<MeteorEntity>of(MeteorEntity::new, MobCategory.MISC).sized(1.2f, 1.2f).clientTrackingRange(24).updateInterval(1)
            .noSave().fireImmune().build(ENTITIES.key("meteor")));
    public static final RegistryObject<EntityType<StarSlashEntity>> STAR_SLASH = ENTITIES.register("star_slash", () ->
        EntityType.Builder.<StarSlashEntity>of(StarSlashEntity::new, MobCategory.MISC).sized(0.6f, 0.6f).clientTrackingRange(8).updateInterval(1)
            .noSave().build(ENTITIES.key("star_slash")));
    public static final RegistryObject<EntityType<StarBoltEntity>> STAR_BOLT = ENTITIES.register("star_bolt", () ->
        EntityType.Builder.<StarBoltEntity>of(StarBoltEntity::new, MobCategory.MISC).sized(0.3f, 0.3f).clientTrackingRange(8).updateInterval(1)
            .setShouldReceiveVelocityUpdates(true).noSave().build(ENTITIES.key("star_bolt")));
    public static final RegistryObject<EntityType<CrystalShardEntity>> CRYSTAL_SHARD = ENTITIES.register("crystal_shard", () ->
        EntityType.Builder.<CrystalShardEntity>of(CrystalShardEntity::new, MobCategory.MISC).sized(0.5f, 0.5f).clientTrackingRange(10).updateInterval(1)
            .setShouldReceiveVelocityUpdates(true).noSave().build(ENTITIES.key("crystal_shard")));
    public static final RegistryObject<EntityType<SingularityEntity>> SINGULARITY = ENTITIES.register("singularity", () ->
        EntityType.Builder.<SingularityEntity>of(SingularityEntity::new, MobCategory.MISC).sized(1.0f, 1.0f).clientTrackingRange(12).updateInterval(2)
            .noSave().fireImmune().build(ENTITIES.key("singularity")));
    public static final RegistryObject<EntityType<SingularityGrenadeEntity>> SINGULARITY_GRENADE = ENTITIES.register("singularity_grenade", () ->
        EntityType.Builder.<SingularityGrenadeEntity>of(SingularityGrenadeEntity::new, MobCategory.MISC).sized(0.25f, 0.25f).clientTrackingRange(4).updateInterval(10)
            .build(ENTITIES.key("singularity_grenade")));

    public static final RegistryObject<EntityType<AstralWispEntity>> ASTRAL_WISP = ENTITIES.register("astral_wisp", () ->
        EntityType.Builder.<AstralWispEntity>of(AstralWispEntity::new, MobCategory.AMBIENT).sized(0.5f, 0.6f).clientTrackingRange(8)
            .build(ENTITIES.key("astral_wisp")));
    public static final RegistryObject<EntityType<VoidStalkerEntity>> VOID_STALKER = ENTITIES.register("void_stalker", () ->
        EntityType.Builder.<VoidStalkerEntity>of(VoidStalkerEntity::new, MobCategory.MONSTER).sized(0.7f, 2.9f).eyeHeight(2.55f).clientTrackingRange(10)
            .build(ENTITIES.key("void_stalker")));
    public static final RegistryObject<EntityType<MeteoriteCrawlerEntity>> METEORITE_CRAWLER = ENTITIES.register("meteorite_crawler", () ->
        EntityType.Builder.<MeteoriteCrawlerEntity>of(MeteoriteCrawlerEntity::new, MobCategory.MONSTER).sized(1.3f, 0.95f).clientTrackingRange(8)
            .fireImmune().build(ENTITIES.key("meteorite_crawler")));
    public static final RegistryObject<EntityType<VoidGazerEntity>> VOID_GAZER = ENTITIES.register("void_gazer", () ->
        EntityType.Builder.<VoidGazerEntity>of(VoidGazerEntity::new, MobCategory.MONSTER).sized(1.1f, 1.1f).eyeHeight(0.55f).clientTrackingRange(10)
            .build(ENTITIES.key("void_gazer")));
    public static final RegistryObject<EntityType<AstraeusEntity>> ASTRAEUS = ENTITIES.register("astraeus", () ->
        EntityType.Builder.<AstraeusEntity>of(AstraeusEntity::new, MobCategory.MONSTER).sized(3.0f, 6.2f).eyeHeight(5.2f).clientTrackingRange(16)
            .fireImmune().build(ENTITIES.key("astraeus")));

    private ModEntities() {}
}
