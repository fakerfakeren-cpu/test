# Scar third-person animation builder

Builds `roblox/rifle/character/ScarCharacterAnims.rbxmx` from the user's R15 rig export, the Rig with the tool equipped saved as glTF. Treat that export as untrusted data and run with `python3 -I`. Needs `numpy` and `Pillow`. The previews also use `../viewmodel_v3/meshrender.py`.

```sh
# Rig + hold + IK + KeyframeSequences; grip.json gets the Tool.Grip the hold was built for
python3 -I build_char.py Export.gltf ScarCharacterAnims.rbxmx grip.json

# Independent check: re-parse, replay through Roblox's joint formula with LookReplication C0 offsets,
# gun hung on RightHand via RightGrip + the new Grip
python3 -I verify_char.py Export.gltf ScarCharacterAnims.rbxmx grip.json

# Previews (GIFs), or one check sheet of reload key moments
python3 -I render_char.py Export.gltf previews_dir
python3 -I render_char.py Export.gltf out_dir check
```

`charcore.py`:
- **Rig:** joint positions, part centres and the exported gun are read from the glTF. `Rig.fk` applies `Part1 = Part0 * C0 * T * C1^-1`, plus the LookReplication offsets when given.
- **Hold:** `search_stance` scored torso yaw and lean, and the gun position, for:
  - reach of both hands;
  - butt in the shoulder;
  - receiver and barrel kept out of the torso and head.

  `BASE_*` hold the chosen hold.
- **IK:** `ArmIK` is a shoulder (3 dof) plus elbow hinge solver, Levenberg-Marquardt with soft terms:
  - an elbow preference;
  - a small wrist bend;
  - frame-to-frame continuity.

  The right hand gets the gun pose through `K_h`, which is fixed in the base hold with a straight wrist. `Poser.grip` turns that into `Tool.Grip`.
- **Animations:** `ANIMS` lists them. Channels are torso offsets, the gun's offset about the pistol grip (in UpperTorso space), and the left-hand target (Body-local or UpperTorso-local keys). They are PCHIP-interpolated and every frame is keyed: 30 fps for Idle, 60 fps for Shoot and Reload.
