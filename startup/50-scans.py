import bluesky.plans as bp
from bluesky.plans import abs_set, trigger, read, run_decorator

@run_decorator()
def waitfor_proton_charge(threshold):
    """Set, trigger, read until the current reaches threshold"""
    i = 0
    while True:
        print("Waiting for Proton Charge (> %f) LOOP %d" % (threshold, i))
        yield from trigger(bs_pcharge, wait=True)
        current_pcharge = yield from read(bs_pcharge)
        if current_pcharge['bs_pcharge']['value'] >= threshold:
            print('DONE')
            break
        i += 1

@run_decorator()
def time_plan(collection_time):
    '''Plan to collect for a period of time'''
    yield from bp.kickoff(detector, wait=True)
    yield from bp.sleep(collection_time)
    yield from bp.complete(detector, wait=True)
    yield from bp.collect(detector)

@run_decorator()
def pcharge_plan(pcharge):
    '''Plan to collection for a given beam current'''
    yield from bp.kickoff(detector, wait=True)
    yield from waitfor_proton_charge(pcharge)
    yield from bp.complete(etector, wait=True)
    yield from bp.collect(detector)

@run_decorator()
def step_scan(mymotor, motor_min, motor_max, motor_step, collection_time):
    "Step mymotor from min -> max with a step size of step and collect for a given time"
    for num in range(motor_min, motor_max, motor_step):
        yield from abs_set(mymotor, num, wait=True)
        yield from time_plan(collection_time)

@run_decorator()
def continuous_step_scan(mymotor, motor_min, motor_max, motor_step, collection_time):
    "Step mymotor, produce a single file."
    # Move to start position
    yield from abs_set(mymotor, motor_min, wait=True)
    # Start
    yield from bp.kickoff(detector, wait=True)
    # and immediately pause
    yield from bp.pause(detector, wait=True)

    for num in range(motor_min, motor_max, motor_step):
        yield from abs_set(mymotor, num, wait=True)
        yield from abs_set(bs_adned_reset_counters, 1, wait=True)
        yield from bp.resume(detector, wait=True)
        yield from bp.sleep(collection_time)
        yield from bp.pause(detector, wait=True)

    yield from bp.complete(detector, wait=True)
    yield from bp.collect(detector)
