// Generated from assurance/03-system/tsc/tsc.yaml by assurance/03-system/tsc/sysml.py.
// Do not edit: edit tsc.yaml and run the generator. A draft by Claude (I0), not reviewed.

package 'WP-S-03 Architecture' {
    doc /* The system architecture of WP-S-03: components with their element (WP-C-04) and derived ASIL, the links between them, the safety mechanisms allocated to them and the functional safety requirements they satisfy, and the redundancies with their common triggering conditions. */
    private import ScalarValues::*;

    part def Component {
        attribute element : String;
        attribute asil : String;
    }
    action def SafetyMechanism {
        attribute asil : String;
    }
    action def Reaction;
    requirement def FunctionalSafetyRequirement;
    connection def Link {
        end part source : Component;
        end part target : Component;
    }
    connection def Redundancy {
        end part channelA : Component;
        end part channelB : Component;
        attribute commonCause : String;
    }

    // Requirements (WP-C-04) and reactions (WP-C-12) the mechanisms refer to.
    requirement 'FSR-01.01' : FunctionalSafetyRequirement { doc /* Limit commanded acceleration to the envelope for the current speed, and to zero or braking whenever the distance to a road user or obstacle ahead detected by EL-03 is below the safe longitudinal distance */ }
    requirement 'FSR-01.02' : FunctionalSafetyRequirement { doc /* Detect actual acceleration above the bounded command from the vehicle state (EL-06), then cut propulsion and brake to standstill within the fault tolerant time interval */ }
    requirement 'FSR-01.03' : FunctionalSafetyRequirement { doc /* Cut propulsion on the safety monitor's command, whatever Autoware commands */ }
    requirement 'FSR-01.05' : FunctionalSafetyRequirement { doc /* Deliver measured speed and longitudinal acceleration to the safety monitor without passing through Autoware, and flag their own faults */ }
    requirement 'FSR-02.01' : FunctionalSafetyRequirement { doc /* Detect road users and obstacles in and beside the vehicle's swept path out to the stopping distance at the maximum ODD speed, by day and night and in the weather of ODD-10 and ODD-11, and report their position and velocity to the monitor */ }
    requirement 'FSR-02.02' : FunctionalSafetyRequirement { doc /* When a detected road user or obstacle is closer than the safe longitudinal distance and the commanded deceleration does not restore it, command the deceleration that does */ }
    requirement 'FSR-02.03' : FunctionalSafetyRequirement { doc /* Compare achieved with commanded deceleration (EL-06) and switch to the secondary braking path on a shortfall */ }
    requirement 'FSR-02.04' : FunctionalSafetyRequirement { doc /* Provide a secondary braking path that can still stop the vehicle after any single fault in the primary one */ }
    requirement 'FSR-03.01' : FunctionalSafetyRequirement { doc /* Keep false detections in the swept path below the rate the SOTIF acceptance criteria allow, so that monitor interventions are rarely unjustified */ }
    requirement 'FSR-03.02' : FunctionalSafetyRequirement { doc /* Limit decelerations from Autoware above the comfortable level that EL-03 does not confirm with a road user or obstacle to a firm, non-emergency level of 3 m/s² (DQ-019 A, DQ-033 A) */ }
    requirement 'FSR-03.03' : FunctionalSafetyRequirement { doc /* Apply emergency-level deceleration on the monitor's own initiative only when FSR-02.02 requires it */ }
    requirement 'FSR-04.01' : FunctionalSafetyRequirement { doc /* Reject steering commands whose predicted swept path, over the stopping time, comes within the safe lateral distance of a road user, obstacle or kerb detected by EL-03, and stop in lane instead */ }
    requirement 'FSR-04.02' : FunctionalSafetyRequirement { doc /* Limit commanded steering angle and rate to the envelope for the current speed */ }
    requirement 'FSR-04.03' : FunctionalSafetyRequirement { doc /* Compare achieved with commanded steering (EL-06) and stop in lane on a deviation beyond the tolerance */ }
    requirement 'FSR-04.04' : FunctionalSafetyRequirement { doc /* Keep steering controllable by wire after any single fault long enough to complete a stop in lane */ }
    requirement 'FSR-04.06' : FunctionalSafetyRequirement { doc /* Deliver measured steering angle to the safety monitor without passing through Autoware, and flag its own faults */ }
    requirement 'FSR-05.01' : FunctionalSafetyRequirement { doc /* At standstill, hold the service brake and park brake until all release conditions hold: doors closed (EL-08), no road user or obstacle detected by EL-03 in the near field in the direction of travel, and a motion request in the selected gear */ }
    requirement 'FSR-05.02' : FunctionalSafetyRequirement { doc /* Detect motion while holding (EL-06) and apply the park brake */ }
    requirement 'FSR-05.03' : FunctionalSafetyRequirement { doc /* Allow reverse only at standstill, on request, and with the rear near field clear as detected by EL-03 */ }
    requirement 'FSR-05.04' : FunctionalSafetyRequirement { doc /* Apply and hold the park brake on the safety monitor's command */ }
    requirement 'FSR-05.05' : FunctionalSafetyRequirement { doc /* Report door state to the safety monitor and inhibit motion with any door open */ }
    requirement 'FSR-06.01' : FunctionalSafetyRequirement { doc /* Do not permit motion whose swept path crosses the predicted path of a road user detected by EL-03 before the vehicle could stop or clear it, using stated bounds on other road users' acceleration and speed (DQ-017 A) */ }
    requirement 'FSR-06.02' : FunctionalSafetyRequirement { doc /* Limit speed where EL-03's view is occluded so that the vehicle can stop for a road user emerging at the assumed maximum speed (DQ-017 A) */ }
    requirement 'FSR-07.01' : FunctionalSafetyRequirement { doc /* Detect loss, delay or implausibility of Autoware's commands within the detection time WP-S-04 allots */ }
    requirement 'FSR-07.02' : FunctionalSafetyRequirement { doc /* On detection, bring the vehicle to a stop in lane with hazard lights on and hold it, without Autoware */ }
    requirement 'FSR-07.03' : FunctionalSafetyRequirement { doc /* Keep the safety monitor, EL-03 and the actuation path powered after any single fault of the Autoware computer's supply */ }
    requirement 'FSR-07.04' : FunctionalSafetyRequirement { doc /* After a minimal risk condition, resume motion only on an explicit release from the remote operations centre with the release conditions of FSR-05.01 met */ }
    requirement 'FSR-07.06' : FunctionalSafetyRequirement { doc /* Brake to a standstill and hold it when commands from the safety monitor stop for longer than the time WP-S-04 sets, whatever Autoware sends (WP-C-12 MRM-5) */ }
    requirement 'FSR-07.07' : FunctionalSafetyRequirement { doc /* On detecting a fault of its own, stop sending commands to the vehicle, so that the vehicle's own stop (FSR-07.06) takes over */ }
    requirement 'FSR-07.08' : FunctionalSafetyRequirement { doc /* When EL-03 fails, have Autoware stop in lane comfortably, check its speed, deceleration and steering against the vehicle state (EL-06), and stop the vehicle itself if it does not slow as expected (DQ-021 A) */ }
    requirement 'FSR-08.01' : FunctionalSafetyRequirement { doc /* In REMOTE mode, reject commands older than the age bound WP-S-04 sets, out of sequence or failing their integrity check, and stop */ }
    requirement 'FSR-08.02' : FunctionalSafetyRequirement { doc /* Apply the same envelope checks to remote commands as to Autoware's (FSR-01.01, FSR-02.02, FSR-04.01, FSR-06.01) */ }
    requirement 'FSR-08.03' : FunctionalSafetyRequirement { doc /* Send every remote driving command with a time stamp, sequence number and integrity protection */ }
    requirement 'FSR-09.01' : FunctionalSafetyRequirement { doc /* Compare the commanded turn indicator with the commanded and achieved steering direction, and switch to hazard lights on a mismatch */ }
    action 'MRM-4' : Reaction;
    action 'MRM-5' : Reaction;
    action 'TR-05' : Reaction;

    // Components (WP-S-03 §2).
    part 'CMP-01' : Component {
        doc /* Autoware computer */
        :>> element = "EL-01";
        :>> asil = "QM";
    }
    part 'CMP-02' : Component {
        doc /* Safety monitor controller */
        :>> element = "EL-02";
        :>> asil = "D";
    }
    part 'CMP-03' : Component {
        doc /* Safety channel processor */
        :>> element = "EL-03";
        :>> asil = "D";
    }
    part 'CMP-04' : Component {
        doc /* Safety LiDAR */
        :>> element = "EL-03";
        :>> asil = "B(D)";
    }
    part 'CMP-05' : Component {
        doc /* Safety radar */
        :>> element = "EL-03";
        :>> asil = "B(D)";
    }
    part 'CMP-06' : Component {
        doc /* Drive-by-wire */
        :>> element = "EL-04";
        :>> asil = "D";
    }
    part 'CMP-07' : Component {
        doc /* Vehicle state sensing */
        :>> element = "EL-06";
        :>> asil = "D";
    }
    part 'CMP-08' : Component {
        doc /* Park brake */
        :>> element = "EL-05";
        :>> asil = "D";
    }
    part 'CMP-09' : Component {
        doc /* Door system */
        :>> element = "EL-08";
        :>> asil = "D";
    }
    part 'CMP-10' : Component {
        doc /* Monitor power supply */
        :>> element = "EL-07";
        :>> asil = "D";
    }
    part 'CMP-11' : Component {
        doc /* Remote operations station */
        :>> element = "EL-09";
        :>> asil = "C";
    }

    // Links (WP-S-03 Figure 2-1).
    connection 'CMP-11 to CMP-02' : Link connect 'CMP-11' to 'CMP-02' { doc /* signed commands, release */ }
    connection 'CMP-01 to CMP-02' : Link connect 'CMP-01' to 'CMP-02' { doc /* commands, heartbeat */ }
    connection 'CMP-04 to CMP-03' : Link connect 'CMP-04' to 'CMP-03';
    connection 'CMP-05 to CMP-03' : Link connect 'CMP-05' to 'CMP-03';
    connection 'CMP-03 to CMP-02' : Link connect 'CMP-03' to 'CMP-02';
    connection 'CMP-02 to CMP-06' : Link connect 'CMP-02' to 'CMP-06' { doc /* bounded commands */ }
    connection 'CMP-07 to CMP-02' : Link connect 'CMP-07' to 'CMP-02';
    connection 'CMP-02 to CMP-08' : Link connect 'CMP-02' to 'CMP-08';
    connection 'CMP-09 to CMP-02' : Link connect 'CMP-09' to 'CMP-02';

    // Safety mechanisms (WP-S-03 §3).
    action 'SM-01' : SafetyMechanism {
        doc /* Longitudinal envelope: Bounds acceleration to the envelope for the current speed, and commands the braking that keeps the safe longitudinal distance to every road user and obstacle the safety channel reports, including across conflict areas and at occlusions; applies the same to remote commands */
        :>> asil = "D";
    }
    allocate 'SM-01' to 'CMP-02';
    dependency 'SM-01 uses' from 'SM-01' to 'CMP-03', 'CMP-07';
    dependency 'SM-01 starts' from 'SM-01' to 'MRM-4';
    satisfy 'FSR-01.01' by 'SM-01';
    satisfy 'FSR-02.02' by 'SM-01';
    satisfy 'FSR-03.03' by 'SM-01';
    satisfy 'FSR-06.01' by 'SM-01';
    satisfy 'FSR-06.02' by 'SM-01';
    satisfy 'FSR-08.02' by 'SM-01';
    action 'SM-02' : SafetyMechanism {
        doc /* Lateral envelope: Bounds steering angle and rate to the envelope for the current speed and rejects steering whose swept path comes within the safe lateral distance of a detected road user, obstacle or kerb */
        :>> asil = "D";
    }
    allocate 'SM-02' to 'CMP-02';
    dependency 'SM-02 uses' from 'SM-02' to 'CMP-03', 'CMP-07';
    dependency 'SM-02 starts' from 'SM-02' to 'MRM-4';
    satisfy 'FSR-04.01' by 'SM-02';
    satisfy 'FSR-04.02' by 'SM-02';
    action 'SM-03' : SafetyMechanism {
        doc /* Achieved-against-commanded monitor: Compares achieved acceleration, deceleration and steering with what was commanded, switches to the secondary brake path on a braking shortfall, and checks Autoware's stop when the safety channel has failed */
        :>> asil = "D";
    }
    allocate 'SM-03' to 'CMP-02';
    dependency 'SM-03 uses' from 'SM-03' to 'CMP-07', 'CMP-06';
    dependency 'SM-03 starts' from 'SM-03' to 'MRM-4';
    satisfy 'FSR-01.02' by 'SM-03';
    satisfy 'FSR-02.03' by 'SM-03';
    satisfy 'FSR-04.03' by 'SM-03';
    satisfy 'FSR-07.08' by 'SM-03';
    action 'SM-04' : SafetyMechanism {
        doc /* Unconfirmed-braking limiter: Holds decelerations above the comfortable level that the safety channel does not confirm to the firm level */
        :>> asil = "C";
    }
    allocate 'SM-04' to 'CMP-02';
    dependency 'SM-04 uses' from 'SM-04' to 'CMP-03';
    satisfy 'FSR-03.02' by 'SM-04';
    action 'SM-05' : SafetyMechanism {
        doc /* Command stream watchdog: Checks every command from Autoware and from remote operations for loss, delay, sequence, age, signature (CSR-01) and plausibility */
        :>> asil = "D";
    }
    allocate 'SM-05' to 'CMP-02';
    dependency 'SM-05 starts' from 'SM-05' to 'MRM-4';
    satisfy 'FSR-07.01' by 'SM-05';
    satisfy 'FSR-08.01' by 'SM-05';
    action 'SM-06' : SafetyMechanism {
        doc /* Stop, hold and release: Brings the vehicle to a stop in lane with hazard lights and holds it, detects motion while holding, gates reverse, and releases only on a verified release with every release condition met */
        :>> asil = "D";
    }
    allocate 'SM-06' to 'CMP-02';
    dependency 'SM-06 uses' from 'SM-06' to 'CMP-06', 'CMP-07', 'CMP-08', 'CMP-09';
    dependency 'SM-06 starts' from 'SM-06' to 'MRM-4';
    satisfy 'FSR-07.02' by 'SM-06';
    satisfy 'FSR-07.04' by 'SM-06';
    satisfy 'FSR-05.01' by 'SM-06';
    satisfy 'FSR-05.02' by 'SM-06';
    satisfy 'FSR-05.03' by 'SM-06';
    action 'SM-07' : SafetyMechanism {
        doc /* Indicator cross-check: Compares the commanded indicator with commanded and achieved steering, and switches to hazard lights on a mismatch */
        :>> asil = "C";
    }
    allocate 'SM-07' to 'CMP-02';
    dependency 'SM-07 uses' from 'SM-07' to 'CMP-07';
    satisfy 'FSR-09.01' by 'SM-07';
    action 'SM-08' : SafetyMechanism {
        doc /* Monitor self-diagnostics and fail-silent output: Detects faults of the monitor's own processor, memory, clock and software (lockstep, memory protection, independent watchdog) and stops its output so the vehicle's own stop takes over */
        :>> asil = "D";
    }
    allocate 'SM-08' to 'CMP-02';
    dependency 'SM-08 starts' from 'SM-08' to 'MRM-5';
    satisfy 'FSR-07.07' by 'SM-08';
    action 'SM-09' : SafetyMechanism {
        doc /* Geometric obstacle detection: Finds road users and obstacles in and beside the swept path from LiDAR and radar returns by geometry and motion, without learned classification, and counts a road user seen by either sensor type (DQ-031 A), each sensor's chain meeting its share of the requirement at ASIL B(D) */
        :>> asil = "D";
    }
    allocate 'SM-09' to 'CMP-03';
    dependency 'SM-09 uses' from 'SM-09' to 'CMP-04', 'CMP-05';
    satisfy 'FSR-02.01' by 'SM-09';
    satisfy 'FSR-03.01' by 'SM-09';
    action 'SM-10' : SafetyMechanism {
        doc /* Safety channel sensor diagnostics: Detects blockage, misalignment, loss and degradation of the safety channel's sensors and reports it to the monitor */
        :>> asil = "D";
    }
    allocate 'SM-10' to 'CMP-03';
    dependency 'SM-10 uses' from 'SM-10' to 'CMP-04', 'CMP-05';
    dependency 'SM-10 starts' from 'SM-10' to 'TR-05';
    satisfy 'FSR-02.01' by 'SM-10';
    action 'SM-11' : SafetyMechanism {
        doc /* Propulsion cut: Cuts propulsion on the monitor's command, whatever else is commanded */
        :>> asil = "D";
    }
    allocate 'SM-11' to 'CMP-06';
    satisfy 'FSR-01.03' by 'SM-11';
    action 'SM-12' : SafetyMechanism {
        doc /* Secondary brake path: Keeps a braking path that can stop the vehicle after any single fault in the primary one */
        :>> asil = "D";
    }
    allocate 'SM-12' to 'CMP-06';
    satisfy 'FSR-02.04' by 'SM-12';
    action 'SM-13' : SafetyMechanism {
        doc /* Fault-tolerant steering for the stop: Keeps steering controllable after any single fault long enough to complete a stop in lane */
        :>> asil = "D";
    }
    allocate 'SM-13' to 'CMP-06';
    satisfy 'FSR-04.04' by 'SM-13';
    action 'SM-14' : SafetyMechanism {
        doc /* Stop on loss of the monitor: Brakes to a standstill and holds it when the monitor's commands stop for longer than WP-S-04 allows */
        :>> asil = "D";
    }
    allocate 'SM-14' to 'CMP-06';
    dependency 'SM-14 starts' from 'SM-14' to 'MRM-5';
    satisfy 'FSR-07.06' by 'SM-14';
    action 'SM-15' : SafetyMechanism {
        doc /* Independent vehicle state: Delivers speed, acceleration and steering angle to the monitor on its own path, with the sensors' own fault flags */
        :>> asil = "D";
    }
    allocate 'SM-15' to 'CMP-07';
    satisfy 'FSR-01.05' by 'SM-15';
    satisfy 'FSR-04.06' by 'SM-15';
    action 'SM-16' : SafetyMechanism {
        doc /* Park brake hold: Applies and holds the park brake on the monitor's command */
        :>> asil = "D";
    }
    allocate 'SM-16' to 'CMP-08';
    satisfy 'FSR-05.04' by 'SM-16';
    action 'SM-17' : SafetyMechanism {
        doc /* Door interlock: Reports door state to the monitor and inhibits motion with any door open */
        :>> asil = "D";
    }
    allocate 'SM-17' to 'CMP-09';
    satisfy 'FSR-05.05' by 'SM-17';
    action 'SM-18' : SafetyMechanism {
        doc /* Independent monitor supply: Keeps the monitor, the safety channel and the actuation path powered after any single fault of the Autoware computer's supply */
        :>> asil = "D";
    }
    allocate 'SM-18' to 'CMP-10';
    satisfy 'FSR-07.03' by 'SM-18';
    action 'SM-19' : SafetyMechanism {
        doc /* Remote command protection: Stamps, numbers and signs every remote command and release before it leaves the station (CSR-01) */
        :>> asil = "C";
    }
    allocate 'SM-19' to 'CMP-11';
    satisfy 'FSR-08.03' by 'SM-19';

    // Redundancy and diversity (WP-S-03 §4).
    connection 'RD-01' : Redundancy connect 'CMP-01' to 'CMP-03' {
        doc /* Autoware's perception and the safety channel's. Diversity: Different sensors (DQ-018 A), learned classification against geometry, different processors and software */
        :>> commonCause = "TC-02, TC-03, TC-04, TC-15, TC-24";
    }
    connection 'RD-02' : Redundancy connect 'CMP-04' to 'CMP-05' {
        doc /* LiDAR and radar inside the safety channel. Diversity: Different physics (light against radio), different failure modes in rain, spray and darkness */
        :>> commonCause = "TC-03, TC-24";
    }
    connection 'RD-03' : Redundancy connect 'CMP-02' to 'CMP-06' {
        doc /* The monitor's stop and the vehicle's own stop when the monitor falls silent. Diversity: Different controllers and suppliers; the vehicle's stop needs only the absence of the monitor's commands */
        :>> commonCause = "TC-25";
    }
    connection 'RD-04' : Redundancy connect 'CMP-06' to 'CMP-06' {
        doc /* Primary and secondary brake paths. Diversity: As the vehicle supplier designs them (AOU-01) */
        :>> commonCause = "TC-25";
    }
}
