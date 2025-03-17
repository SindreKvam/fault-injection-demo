library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_level is
    port (
        MAX10_CLK1_50 : in std_logic;
        KEY : in std_logic_vector(1 downto 0);
        --------------------------------------------------
        -- Output
        --------------------------------------------------
        LED         : out std_logic_vector(9 downto 0)    := (others => '0');
        --------------------------------------------------
        -- IO
        --------------------------------------------------
        ARDUINO_IO  : inout std_logic_vector(15 downto 0) := (others => '0')
    );
end top_level;

architecture rtl of top_level is

    --------------------------------------------------
    -- Registers
    --------------------------------------------------
    signal counter_reg  : std_logic_vector(31 downto 0) := (others => '0');
    signal glitch_sig   : std_logic                     := '0';

    signal uart_data  : std_logic_vector(7 downto 0) := (others => '0');
    signal uart_valid : std_logic                    := '0';
    signal uart_rx    : std_logic                    := '0';
    signal uart_tx    : std_logic                    := '0';

    -- UART accessible registers
    signal glitch_delay : std_logic_vector(31 downto 0);

    --------------------------------------------------
    -- Create state machine
    --------------------------------------------------
    type t_state is (IDLE, GLITCH, HOLDOFF);
    signal state : t_state := IDLE;

    --------------------------------------------------
    -- Constants
    --------------------------------------------------
    constant C_HOLD_TIME : std_logic_vector(31 downto 0) := std_logic_vector(to_unsigned(10000000, 32));
    constant C_CLK_HZ    : integer                       := 50e6;
    constant C_BAUD_RATE : integer                       := 115200;

begin

    -- Renaming
    ARDUINO_IO(0) <= glitch_sig; -- ARDUINO_IO(0) is an output
    uart_rx <= ARDUINO_IO(1);    -- ARDUINO_IO(1) is an input
    ARDUINO_IO(2) <= uart_tx;    -- ARDUINO_IO(2) is an output

    LED <= glitch_delay(9 downto 0);

    --------------------------------------------------
    -- UART configuration
    --------------------------------------------------
    -- Generated with the command:
    -- python uart_regs-1.0.4/gen_uart_regs.py glitch_delay=32:out:std_logic_vector
    UART_REGS_INST : entity work.uart_regs(rtl)
    generic map (
        clk_hz => C_CLK_HZ,
        baud_rate => C_BAUD_RATE
    )
    port map (
        clk => MAX10_CLK1_50,
        rst => not KEY(1),
        uart_rx => uart_rx,
        uart_tx => uart_tx,
        glitch_delay => glitch_delay
    );

    --------------------------------------------------
    -- Main process
    --------------------------------------------------
    MAIN_PROC : process(MAX10_CLK1_50)

        variable v_led_reg : std_logic_vector(9 downto 0);
        variable v_counter_reg : std_logic_vector(31 downto 0);
        variable v_glitch_sig : std_logic;

    begin

        if rising_edge(MAX10_CLK1_50) then

            -- Initialize variables
            v_led_reg       := (others => '0');
            v_counter_reg   := (others => '0');
            v_glitch_sig    := '1';
            
            --------------------------------------------------
            -- State machine
            --------------------------------------------------
            case state is 
                --------------------------------------------------
                when IDLE =>
                    --------------------------------------------------
                    v_led_reg(1 downto 0) := "11";

                    if (KEY(0) = '0') then
                        state <= GLITCH;
                    end if;

                --------------------------------------------------
                when GLITCH =>
                    -- Set glitch signal to low to turn off power
                    --------------------------------------------------
                    v_glitch_sig := '0';
                    
                    if (counter_reg >= glitch_delay) then
                        state <= HOLDOFF;
                        -- Will also set counter to 0
                    else
                        v_counter_reg := std_logic_vector(unsigned(counter_reg) + 1);
                    end if;

                --------------------------------------------------
                when HOLDOFF =>
                    -- This state is a debounce for the button press
                    --------------------------------------------------
                    v_led_reg(1 downto 0) := "10";

                    if (counter_reg >= C_HOLD_TIME) then
                        state <= IDLE;
                    else
                        v_counter_reg := std_logic_vector(unsigned(counter_reg) + 1);
                    end if;

            end case;
            
            -- Assign variables to signals
            counter_reg     <= v_counter_reg;
            glitch_sig      <= v_glitch_sig;

        end if;
        
    end process;

end architecture;