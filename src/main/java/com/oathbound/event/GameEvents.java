package com.oathbound.event;

import com.oathbound.Config;
import com.oathbound.block.WisplightBlock;
import com.oathbound.item.WardensLanternItem;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.*;
import com.oathbound.util.Vfx;
import com.oathbound.util.Puzzles;
import com.oathbound.util.Scheduler;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.EntityTypeTags;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** Server-side gameplay glue: lantern light, Gloamrot, set bonuses, weapon on-hit effects and veil travel. */
public final class GameEvents {
    private static final Identifier STEADFAST_ID = Identifier.fromNamespaceAndPath(com.oathbound.Oathbound.MODID, "steadfast");
    private static final Map<UUID, float[]> RIPOSTE = new HashMap<>();
    private static final Map<UUID, Long> STEADFAST_COOLDOWN = new HashMap<>();
    private static final Map<UUID, Integer> VEIL_TICKS = new HashMap<>();
    private static final Map<UUID, Long> VEIL_COOLDOWN = new HashMap<>();
    private static final ThreadLocal<Boolean> IN_CHARGE = ThreadLocal.withInitial(() -> false);

    private GameEvents() {}

    // ------------------------------------------------------------------ armour checks
    private static boolean wearing(LivingEntity e, EquipmentSlot slot, net.minecraft.world.item.Item item) {
        return e.getItemBySlot(slot).is(item);
    }

    public static boolean hasOathsteelSet(LivingEntity e) {
        return wearing(e, EquipmentSlot.HEAD, ModItems.OATHSTEEL_HELMET.get()) && wearing(e, EquipmentSlot.CHEST, ModItems.OATHSTEEL_CHESTPLATE.get())
            && wearing(e, EquipmentSlot.LEGS, ModItems.OATHSTEEL_LEGGINGS.get()) && wearing(e, EquipmentSlot.FEET, ModItems.OATHSTEEL_BOOTS.get());
    }

    public static boolean hasArcanistSet(LivingEntity e) {
        return wearing(e, EquipmentSlot.HEAD, ModItems.ARCANIST_HOOD.get()) && wearing(e, EquipmentSlot.CHEST, ModItems.ARCANIST_ROBE.get())
            && wearing(e, EquipmentSlot.LEGS, ModItems.ARCANIST_LEGGINGS.get()) && wearing(e, EquipmentSlot.FEET, ModItems.ARCANIST_BOOTS.get());
    }

    public static boolean wearsCrown(LivingEntity e) {
        return e != null && wearing(e, EquipmentSlot.HEAD, ModItems.HOLLOW_CROWN.get());
    }

    public static ItemStack heldLitLantern(Player p) {
        for (ItemStack s : new ItemStack[]{p.getMainHandItem(), p.getOffhandItem()}) {
            if (s.getItem() instanceof WardensLanternItem l && l.isLit(s)) return s;
        }
        return ItemStack.EMPTY;
    }

    // ------------------------------------------------------------------ ticks
    public static void levelTick(ServerLevel level) {
        Scheduler.tick(level);
        com.oathbound.entity.npc.PilgrimVisits.tick(level);
    }

    public static void onPlayerTick(Player player) {
        if (!(player instanceof ServerPlayer sp) || !(player.level() instanceof ServerLevel level) || !player.isAlive()) return;
        tickVeil(sp, level);
        int t = player.tickCount;
        if (t % 40 == 7) com.oathbound.quest.Codex.discover(sp);

        if (t % 4 == 0 && Config.lanternLight()) {
            ItemStack lantern = heldLitLantern(player);
            if (!lantern.isEmpty()) {
                WisplightBlock.place(level, BlockPos.containing(player.getEyePosition()), false);
                if (t % 300 == 0) ((WardensLanternItem) lantern.getItem()).burn(lantern, player, 1);
            }
        }

        if (t % 20 == 0) {
            // Steadfast: full Oathsteel makes you immovable.
            AttributeInstance kb = player.getAttribute(Attributes.KNOCKBACK_RESISTANCE);
            if (kb != null) {
                boolean want = hasOathsteelSet(player);
                boolean has = kb.getModifier(STEADFAST_ID) != null;
                if (want && !has) kb.addTransientModifier(new AttributeModifier(STEADFAST_ID, 1.0, AttributeModifier.Operation.ADD_VALUE));
                else if (!want && has) kb.removeModifier(STEADFAST_ID);
            }
            if (wearsCrown(player)) player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 320, 0, true, false, true));
            applyBoons(sp, level);
            GearEvents.tick(sp, level);
        }
        // Arcanist: feather-fall while sneaking in the air.
        if (player.isShiftKeyDown() && !player.onGround() && player.getDeltaMovement().y < -0.1 && hasArcanistSet(player)) {
            player.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 10, 0, true, false, false));
        }

        if (t % 40 == 0 && level.dimension() == ModWorldgen.GLOAMING && Config.gloamrot() && !player.isCreative() && !player.isSpectator()) {
            tickGloamrot(sp, level);
        }
        if (t % 100 == 0) sunmend(player, level);
    }

    private static void tickGloamrot(ServerPlayer player, ServerLevel level) {
        if (player.hasEffect(ModEffects.holder(ModEffects.RADIANCE)) || wearsCrown(player) || QuestLog.hasBoon(player, "veilwalker")
            || GearEvents.fullSet(player, GearEvents.Tier.DAWNSTEEL)) return;
        ItemStack lantern = ItemStack.EMPTY;
        var inv = player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.getItem() instanceof WardensLanternItem l && l.isLit(s)) {
                if (l.isEverflame()) return;
                lantern = s;
            }
        }
        if (!lantern.isEmpty()) {
            ((WardensLanternItem) lantern.getItem()).burn(lantern, player, 1);
            return;
        }
        boolean fresh = !player.hasEffect(ModEffects.holder(ModEffects.GLOAMROT));
        player.addEffect(new MobEffectInstance(ModEffects.holder(ModEffects.GLOAMROT), 120, 0));
        if (fresh) player.sendOverlayMessage(Component.translatable("message.oathbound.gloamrot").withStyle(ChatFormatting.DARK_PURPLE));
    }

    /** Oathsteel tools and armour slowly mend themselves in daylight. */
    private static void sunmend(Player player, ServerLevel level) {
        if (!level.isBrightOutside() || level.getBrightness(LightLayer.SKY, player.blockPosition()) < 14) return;
        var inv = player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.isDamaged() && s.is(ModTags.SUNMENDED)) s.setDamageValue(s.getDamageValue() - 1);
        }
    }


    // ------------------------------------------------------------------ Oath Boons
    private static final Identifier BOON_ID = Identifier.fromNamespaceAndPath(com.oathbound.Oathbound.MODID, "boon");
    private static final Map<UUID, Long> HOUSECARL_OATH = new HashMap<>();

    private static void modifier(Player p, net.minecraft.core.Holder<net.minecraft.world.entity.ai.attributes.Attribute> attr, String name, double amount,
                                 AttributeModifier.Operation op, boolean active) {
        AttributeInstance inst = p.getAttribute(attr);
        if (inst == null) return;
        Identifier id = BOON_ID.withSuffix("/" + name);
        boolean has = inst.getModifier(id) != null;
        if (active && !has) inst.addTransientModifier(new AttributeModifier(id, amount, op));
        else if (!active && has) inst.removeModifier(id);
    }

    private static void applyBoons(ServerPlayer p, ServerLevel level) {
        var add = AttributeModifier.Operation.ADD_VALUE;
        var mul = AttributeModifier.Operation.ADD_MULTIPLIED_BASE;
        modifier(p, Attributes.MAX_HEALTH, "vigor", 4.0, add, QuestLog.hasBoon(p, "squires_vigor"));
        modifier(p, Attributes.MOVEMENT_SPEED, "stride", 0.08, mul, QuestLog.hasBoon(p, "pilgrims_stride"));
        boolean reach = QuestLog.hasBoon(p, "long_reach");
        modifier(p, Attributes.ENTITY_INTERACTION_RANGE, "reach", 1.0, add, reach);
        modifier(p, Attributes.BLOCK_INTERACTION_RANGE, "reach_block", 1.0, add, reach);
        modifier(p, Attributes.LUCK, "luck", 2.0, add, QuestLog.hasBoon(p, "scholars_luck"));
        boolean king = QuestLog.hasBoon(p, "kingsblood");
        modifier(p, Attributes.ARMOR, "kingsblood", 2.0, add, king);
        modifier(p, Attributes.ARMOR_TOUGHNESS, "kingsblood_t", 2.0, add, king);
        modifier(p, Attributes.ATTACK_DAMAGE, "gatesworn", 0.15, mul, QuestLog.hasBoon(p, "gatesworn"));
        modifier(p, Attributes.SAFE_FALL_DISTANCE, "featherfall", 5.0, add, QuestLog.hasBoon(p, "featherfall"));
        if (QuestLog.hasBoon(p, "tidebound") && p.isInWater()) {
            p.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 60, 0, true, false, true));
            p.addEffect(new MobEffectInstance(MobEffects.DOLPHINS_GRACE, 60, 0, true, false, true));
        }
        if (QuestLog.hasBoon(p, "grave_sight") && p.getY() < level.getSeaLevel() - 8 && !level.canSeeSky(p.blockPosition())) {
            p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 320, 0, true, false, true));
        }
        if (QuestLog.hasBoon(p, "everflame_heart")) p.addEffect(new MobEffectInstance(ModEffects.holder(ModEffects.RADIANCE), 60, 0, true, false, true));
        if (QuestLog.hasBoon(p, "dawnbound") && level.isBrightOutside() && level.canSeeSky(p.blockPosition())) {
            p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 60, 0, true, false, true));
        }
    }

    /** Cooldown for Oathbound abilities, shortened by Arcanist regalia and the Arcane Insight boon. */
    public static int cooldown(Player p, int base) {
        double f = 1.0;
        if (hasArcanistSet(p)) f *= 0.5;
        if (p instanceof ServerPlayer sp && QuestLog.hasBoon(sp, "arcane_insight")) f *= 0.75;
        return Math.max(1, (int) Math.round(base * f));
    }

    // ------------------------------------------------------------------ the veil
    private static void tickVeil(ServerPlayer player, ServerLevel level) {
        UUID id = player.getUUID();
        boolean inside = level.getBlockState(player.blockPosition()).is(ModBlocks.GLOAM_VEIL.get())
            || level.getBlockState(BlockPos.containing(player.getEyePosition())).is(ModBlocks.GLOAM_VEIL.get());
        Long cd = VEIL_COOLDOWN.get(id);
        if (!inside) {
            VEIL_TICKS.remove(id);
            if (cd != null && level.getGameTime() - cd > 20) VEIL_COOLDOWN.remove(id);
            return;
        }
        if (cd != null) return;
        int n = VEIL_TICKS.merge(id, 1, Integer::sum);
        Vfx.spiralIn(level, ModParticles.GLOAM_WISP.get(), player.position().add(0, 1, 0), 2.0, 3, n);
        if (n == 1) level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.GATE_HUM.get(), SoundSource.PLAYERS, 1.0f, 0.7f);
        if (n == 10) player.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 80, 0, true, false, false));
        if (n >= 40) {
            VEIL_TICKS.remove(id);
            VEIL_COOLDOWN.put(id, level.getGameTime());
            if (level.dimension() == ModWorldgen.GLOAMING) GloamingTravel.toOverworld(player);
            else GloamingTravel.toGloaming(player, player.blockPosition());
        }
    }

    // ------------------------------------------------------------------ combat
    public static void onLivingHurt(LivingHurtEvent event) {
        LivingEntity victim = event.getEntity();
        if (!(victim.level() instanceof ServerLevel level)) return;
        float amount = event.getAmount();

        if (victim.hasEffect(ModEffects.holder(ModEffects.SUNMARK))) amount *= 1.3f;

        Entity src = event.getSource().getEntity();
        if (src instanceof Player attacker && event.getSource().getDirectEntity() == attacker) {
            amount = GearEvents.outgoing(level, attacker, victim, amount);
            ItemStack weapon = attacker.getMainHandItem();
            if (weapon.is(ModItems.OATHSTEEL_LONGSWORD.get())) {
                float[] stored = RIPOSTE.remove(attacker.getUUID());
                if (stored != null && level.getGameTime() - (long) stored[1] <= 60) {
                    amount += stored[0];
                    level.playSound(null, victim.getX(), victim.getY(), victim.getZ(), ModSounds.RIPOSTE.get(), SoundSource.PLAYERS, 1.2f, 1.0f);
                    Vfx.burst(level, ModParticles.EMBER.get(), victim.getBoundingBox().getCenter(), 20, 0.3, 0.15);
                    Vfx.burst(level, ParticleTypes.CRIT, victim.getBoundingBox().getCenter(), 12, 0.3, 0.3);
                }
            } else if (weapon.is(ModItems.WARDENS_HALBERD.get()) && attacker.isSprinting() && !IN_CHARGE.get()) {
                chargeThrust(level, attacker, victim, amount);
            } else if (weapon.is(ModItems.SHADOWREAP_SICKLE.get())) {
                int light = level.getMaxLocalRawBrightness(victim.blockPosition());
                float dark = (15 - light) / 15f;
                amount *= 1.0f + dark * 0.6f;
                attacker.heal(amount * (0.05f + dark * 0.15f));
                if (dark > 0.4f) {
                    level.playSound(null, victim.getX(), victim.getY(), victim.getZ(), ModSounds.SICKLE_REAP.get(), SoundSource.PLAYERS, 0.8f, 1.0f + dark * 0.3f);
                    Vfx.line(level, ModParticles.GLOAM_WISP.get(), victim.getBoundingBox().getCenter(), attacker.position().add(0, 1, 0), 0.4);
                }
            } else if (weapon.is(ModItems.DAWNBREAKER.get())) {
                if (victim.typeHolder().is(ModTags.GLOAM_CREATURES) || victim.typeHolder().is(EntityTypeTags.UNDEAD)) {
                    amount *= 1.5f;
                    victim.igniteForSeconds(4);
                    Vfx.burst(level, ModParticles.SUNBURST.get(), victim.getBoundingBox().getCenter(), 10, 0.3, 0.1);
                }
            }
        }

        if (src instanceof ServerPlayer sp && victim instanceof com.oathbound.entity.boss.KeeperEntity && QuestLog.hasBoon(sp, "kingslayer")) amount *= 1.2f;
        if (victim instanceof ServerPlayer sp) {
            if (QuestLog.hasBoon(sp, "knights_guard") && src != null && event.getSource().getDirectEntity() == src) amount *= 0.9f;
            if (QuestLog.hasBoon(sp, "glyphskin") && event.getSource().is(net.minecraft.tags.DamageTypeTags.WITCH_RESISTANT_TO)) amount *= 0.8f;
            if (QuestLog.hasBoon(sp, "oath_of_the_housecarl") && sp.getHealth() - amount < sp.getMaxHealth() * 0.3f) {
                Long last = HOUSECARL_OATH.get(sp.getUUID());
                if (last == null || level.getGameTime() - last > 2400) {
                    HOUSECARL_OATH.put(sp.getUUID(), level.getGameTime());
                    var h = ModEntities.SPECTRAL_HOUSECARL.get().create(level, net.minecraft.world.entity.EntitySpawnReason.MOB_SUMMONED);
                    if (h != null) {
                        h.snapTo(sp.getX() + 1, sp.getY(), sp.getZ() + 1, sp.getYRot(), 0);
                        h.makeAlly(sp, 600);
                        level.addFreshEntity(h);
                        Vfx.column(level, ModParticles.SPIRIT.get(), h.position(), 3, 30);
                        level.playSound(null, sp.getX(), sp.getY(), sp.getZ(), ModSounds.WARHORN.get(), SoundSource.PLAYERS, 1.5f, 1.3f);
                    }
                }
            }
        }
        if (victim instanceof Player player) {
            amount = GearEvents.incoming(player, event.getSource(), amount);
            // Riposte: remember what was taken, to pay it back.
            if (player.getMainHandItem().is(ModItems.OATHSTEEL_LONGSWORD.get())) {
                float[] prev = RIPOSTE.get(player.getUUID());
                float stored = Math.min(8f, (prev != null && level.getGameTime() - (long) prev[1] <= 60 ? prev[0] : 0f) + amount * 0.75f);
                RIPOSTE.put(player.getUUID(), new float[]{stored, level.getGameTime()});
            }
            if (hasOathsteelSet(player) && player.getHealth() - amount < player.getMaxHealth() * 0.3f) {
                Long last = STEADFAST_COOLDOWN.get(player.getUUID());
                if (last == null || level.getGameTime() - last > 1200) {
                    STEADFAST_COOLDOWN.put(player.getUUID(), level.getGameTime());
                    player.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 120, 1));
                    level.playSound(null, player.getX(), player.getY(), player.getZ(), net.minecraft.sounds.SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 0.6f, 1.6f);
                    Vfx.ring(level, ModParticles.EMBER.get(), player.position().add(0, 0.2, 0), 1.5, 24, 0.1);
                    player.sendOverlayMessage(Component.translatable("message.oathbound.steadfast").withStyle(ChatFormatting.GOLD));
                }
            }
        }
        event.setAmount(amount);
    }

    private static void chargeThrust(ServerLevel level, Player attacker, LivingEntity victim, float amount) {
        IN_CHARGE.set(true);
        try {
            Vec3 from = attacker.getEyePosition().add(0, -0.4, 0);
            Vec3 dir = attacker.getLookAngle().multiply(1, 0, 1).normalize();
            Vec3 to = from.add(dir.scale(5));
            Vfx.line(level, ParticleTypes.SWEEP_ATTACK, from.add(dir), to, 1.2);
            Vfx.line(level, ModParticles.EMBER.get(), from, to, 0.3);
            level.playSound(null, attacker.getX(), attacker.getY(), attacker.getZ(), ModSounds.HALBERD_THRUST.get(), SoundSource.PLAYERS, 1.2f, 1.0f);
            for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(from, to).inflate(1.2), e -> e != attacker && e.isAlive())) {
                Vec3 c = e.getBoundingBox().getCenter();
                Vec3 seg = to.subtract(from);
                double tt = Math.max(0, Math.min(1, c.subtract(from).dot(seg) / seg.lengthSqr()));
                if (from.add(seg.scale(tt)).distanceTo(c) > 1.4) continue;
                if (e instanceof Player p && !com.oathbound.item.Inscriptions.isFoeOf(p, attacker)) continue;
                if (e instanceof net.minecraft.world.entity.TamableAnimal pet && pet.isOwnedBy(attacker)) continue;
                if (e != victim) e.hurtServer(level, level.damageSources().playerAttack(attacker), amount * 0.6f);
                e.setDeltaMovement(e.getDeltaMovement().add(dir.scale(0.9)).add(0, 0.25, 0));
                e.hurtMarked = true;
            }
        } finally {
            IN_CHARGE.set(false);
        }
    }

    // ------------------------------------------------------------------ sealed keeps
    /**
     * Every boss's lair and the boss whose defeat lifts its seal: until then its stones cannot be broken or
     * blasted, so nobody digs round a ward or into an arena.
     */
    private static final Map<net.minecraft.resources.ResourceKey<net.minecraft.world.level.levelgen.structure.Structure>, String> SEALED = Map.of(
        lair("drowned_chapel"), "caldris", lair("arcanist_spire"), "veyl", lair("barrow_of_kings"), "hrodgar",
        lair("grove_shrine"), "grove_king", lair("bog_hut"), "bog_mother", lair("cinder_sanctum"), "cinder_colossus");
    /** The Hollow Throne is raised in the Gloaming by hand, not as a structure: its arena is this radius around the throne. */
    private static final double THRONE_RADIUS = 36;

    private static net.minecraft.resources.ResourceKey<net.minecraft.world.level.levelgen.structure.Structure> lair(String id) {
        return net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.STRUCTURE,
            net.minecraft.resources.Identifier.fromNamespaceAndPath(com.oathbound.Oathbound.MODID, id));
    }

    /** The boss quest that guards this position, or null outside every lair. */
    public static String sealedBy(ServerLevel level, BlockPos pos) {
        if (level.dimension() == ModWorldgen.GLOAMING) {
            double dx = pos.getX() - GloamingTravel.THRONE.getX(), dz = pos.getZ() - GloamingTravel.THRONE.getZ();
            return dx * dx + dz * dz < THRONE_RADIUS * THRONE_RADIUS ? "morvane" : null;
        }
        if (level.dimension() != net.minecraft.world.level.Level.OVERWORLD) return null;
        for (var e : SEALED.entrySet()) {
            var key = e.getKey();
            if (level.structureManager().getStructureWithPieceAt(pos, h -> h.is(key)).isValid()) return e.getValue();
        }
        return null;
    }

    /** Survival players cannot dig into a keep before they have beaten its keeper. Returns true to cancel. */
    public static boolean onBreak(net.minecraftforge.event.level.BlockEvent.BreakEvent event) {
        if (!(event.getLevel() instanceof ServerLevel level) || !(event.getPlayer() instanceof ServerPlayer p) || p.isCreative()) return false;
        if (event.getState().getDestroySpeed(level, event.getPos()) == 0) return false;
        String keeper = sealedBy(level, event.getPos());
        if (keeper == null || QuestLog.isComplete(p, keeper)) return false;
        p.sendOverlayMessage(Component.translatable("message.oathbound.sealed_stone").withStyle(ChatFormatting.LIGHT_PURPLE));
        return true;
    }

    /** Explosions (creepers, TNT, a keeper's own blasts) leave the keeps' stones standing. */
    public static void onDetonate(net.minecraftforge.event.level.ExplosionEvent.Detonate event) {
        if (!(event.getLevel() instanceof ServerLevel level)) return;
        event.getAffectedBlocks().removeIf(pos -> sealedBy(level, pos) != null);
    }

    // ------------------------------------------------------------------ joining & travelling
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !Config.giveChronicle()) return;
        CompoundTag root = player.getPersistentData();
        CompoundTag persisted = root.getCompoundOrEmpty("PlayerPersisted");
        if (persisted.getBooleanOr("oathbound_chronicle", false)) return;
        persisted.putBoolean("oathbound_chronicle", true);
        root.put("PlayerPersisted", persisted);
        ItemStack book = new ItemStack(ModItems.LANTERN_CHRONICLE.get());
        if (!player.getInventory().add(book)) player.drop(book, false);
        player.sendSystemMessage(Component.translatable("message.oathbound.welcome").withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC));
    }

    public static void onChangedDimension(PlayerEvent.PlayerChangedDimensionEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getTo() == ModWorldgen.GLOAMING) {
            QuestLog.grant(player, "gloaming", "entered");
        }
    }

    /** Sunmark: glowing + 30% more damage for {@code ticks}. */
    public static void sunmark(LivingEntity e, int ticks) {
        e.addEffect(new MobEffectInstance(ModEffects.holder(ModEffects.SUNMARK), ticks, 0));
        e.addEffect(new MobEffectInstance(MobEffects.GLOWING, ticks, 0));
    }

    public static boolean isLit(ServerLevel level, BlockPos pos) {
        return level.getMaxLocalRawBrightness(pos) >= 10 || !Puzzles.find(level, pos, 0, ModBlocks.WISPLIGHT.get()).isEmpty();
    }
}
