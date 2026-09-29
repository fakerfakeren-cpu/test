package com.rimeheart.registry;

import com.rimeheart.Rimeheart;
import com.rimeheart.entity.boss.FrostSovereignEntity;
import com.rimeheart.entity.mob.FrostWraithEntity;
import com.rimeheart.entity.mob.ShardlingEntity;
import com.rimeheart.entity.projectile.FrostChargeEntity;
import com.rimeheart.entity.projectile.IceShardEntity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, Rimeheart.MODID);

    public static final RegistryObject<EntityType<IceShardEntity>> ICE_SHARD = ENTITIES.register("ice_shard", () ->
        EntityType.Builder.<IceShardEntity>of(IceShardEntity::new, MobCategory.MISC).sized(0.4f, 0.4f).clientTrackingRange(10).updateInterval(1)
            .setShouldReceiveVelocityUpdates(true).noSave().build(ENTITIES.key("ice_shard")));
    public static final RegistryObject<EntityType<FrostChargeEntity>> FROST_CHARGE = ENTITIES.register("frost_charge", () ->
        EntityType.Builder.<FrostChargeEntity>of(FrostChargeEntity::new, MobCategory.MISC).sized(0.25f, 0.25f).clientTrackingRange(4).updateInterval(10)
            .build(ENTITIES.key("frost_charge")));

    public static final RegistryObject<EntityType<FrostWraithEntity>> FROST_WRAITH = ENTITIES.register("frost_wraith", () ->
        EntityType.Builder.<FrostWraithEntity>of(FrostWraithEntity::new, MobCategory.MONSTER).sized(0.8f, 1.9f).eyeHeight(1.6f).clientTrackingRange(10)
            .build(ENTITIES.key("frost_wraith")));
    public static final RegistryObject<EntityType<ShardlingEntity>> SHARDLING = ENTITIES.register("shardling", () ->
        EntityType.Builder.<ShardlingEntity>of(ShardlingEntity::new, MobCategory.MONSTER).sized(0.7f, 0.5f).eyeHeight(0.3f).clientTrackingRange(8)
            .build(ENTITIES.key("shardling")));
    public static final RegistryObject<EntityType<FrostSovereignEntity>> FROST_SOVEREIGN = ENTITIES.register("frost_sovereign", () ->
        EntityType.Builder.<FrostSovereignEntity>of(FrostSovereignEntity::new, MobCategory.MONSTER).sized(2.4f, 5.2f).eyeHeight(4.4f).clientTrackingRange(16)
            .fireImmune().build(ENTITIES.key("frost_sovereign")));

    private ModEntities() {}
}
