
enable_pwm() {
    echo 1 > /sys/class/fusion_hat/fusion_hat/pwm/pwm$1/enable
}

get_pwm_enabled() {
    cat /sys/class/fusion_hat/fusion_hat/pwm/pwm$1/enable
}

set_pwm_period() {
    echo $2 > /sys/class/fusion_hat/fusion_hat/pwm/pwm$1/period
}

get_pwm_period() {
    cat /sys/class/fusion_hat/fusion_hat/pwm/pwm$1/period
}

set_pwm_duty_cycle() {
    echo $2 > /sys/class/fusion_hat/fusion_hat/pwm/pwm$1/duty_cycle
}

get_pwm_duty_cycle() {
    cat /sys/class/fusion_hat/fusion_hat/pwm/pwm$1/duty_cycle
}

test_pwm() {
    echo "Enable PWM $1"
    enable_pwm $1
    echo "PWM0 enabled: $(get_pwm_enabled $1)"

    echo "Set PWM $1 period to 20000"
    set_pwm_period $1 20000
    echo "PWM $1 period: $(get_pwm_period $1)"

    for i in {0..200}
    do
        v=$((i * 100))
        echo "Set PWM $1 duty cycle to $v"
        set_pwm_duty_cycle $1 $v
        echo "PWM $1 duty cycle: $(get_pwm_duty_cycle $1)"
        sleep 0.001
    done
}

test_pwm 1