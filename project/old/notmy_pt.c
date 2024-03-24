		// If the current signal is above one of the thresholds (integral or filtered signal), it's a peak candidate.
        if (integral[current] >= threshold_i1 || highpass[current] >= threshold_f1)
        {
            peak_i = integral[current];
            peak_f = highpass[current];
        }

		// If both the integral and the signal are above their thresholds, they're probably signal peaks.
		if ((integral[current] >= threshold_i1) && (highpass[current] >= threshold_f1))
		{
			// There's a 200ms latency. If the new peak respects this condition, we can keep testing.
			if (sample > lastQRS + FS/5)
			{
			    // If it respects the 200ms latency, but it doesn't respect the 360ms latency, we check the slope.
				if (sample <= lastQRS + (long unsigned int)(0.36*FS))
				{
				    // The squared slope is "M" shaped. So we have to check nearby samples to make sure we're really looking
				    // at its peak value, rather than a low one.
				    currentSlope = 0;
				    for (j = current - 10; j <= current; j++)
                        if (squared[j] > currentSlope)
                            currentSlope = squared[j];

				    if (currentSlope <= (dataType)(lastSlope/2))
                    {
                        qrs = false;
                    }

                    else
                    {
                        spk_i = 0.125*peak_i + 0.875*spk_i;
                        threshold_i1 = npk_i + 0.25*(spk_i - npk_i);
                        threshold_i2 = 0.5*threshold_i1;

                        spk_f = 0.125*peak_f + 0.875*spk_f;
                        threshold_f1 = npk_f + 0.25*(spk_f - npk_f);
                        threshold_f2 = 0.5*threshold_f1;

                        lastSlope = currentSlope;
                        qrs = true;
                    }
				}
				// If it was above both thresholds and respects both latency periods, it certainly is a R peak.
				else
				{
				    currentSlope = 0;
                    for (j = current - 10; j <= current; j++)
                        if (squared[j] > currentSlope)
                            currentSlope = squared[j];

                    spk_i = 0.125*peak_i + 0.875*spk_i;
                    threshold_i1 = npk_i + 0.25*(spk_i - npk_i);
                    threshold_i2 = 0.5*threshold_i1;

                    spk_f = 0.125*peak_f + 0.875*spk_f;
                    threshold_f1 = npk_f + 0.25*(spk_f - npk_f);
                    threshold_f2 = 0.5*threshold_f1;

                    lastSlope = currentSlope;
                    qrs = true;
				}
			}
			// If the new peak doesn't respect the 200ms latency, it's noise. Update thresholds and move on to the next sample.
			else
            {
                peak_i = integral[current];
				npk_i = 0.125*peak_i + 0.875*npk_i;
				threshold_i1 = npk_i + 0.25*(spk_i - npk_i);
				threshold_i2 = 0.5*threshold_i1;
				peak_f = highpass[current];
				npk_f = 0.125*peak_f + 0.875*npk_f;
				threshold_f1 = npk_f + 0.25*(spk_f - npk_f);
                threshold_f2 = 0.5*threshold_f1;
                qrs = false;
				outputSignal[current] = qrs;
				if (sample > DELAY + BUFFSIZE)
                	output(outputSignal[0]);
                continue;
            }

		}

		// If a R-peak was detected, the RR-averages must be updated.
		if (qrs)
		{
			// Add the newest RR-interval to the buffer and get the new average.
			rravg1 = 0;
			for (i = 0; i < 7; i++)
			{
				rr1[i] = rr1[i+1];
				rravg1 += rr1[i];
			}
			rr1[7] = sample - lastQRS;
			lastQRS = sample;
			rravg1 += rr1[7];
			rravg1 *= 0.125;

			// If the newly-discovered RR-average is normal, add it to the "normal" buffer and get the new "normal" average.
			// Update the "normal" beat parameters.
			if ( (rr1[7] >= rrlow) && (rr1[7] <= rrhigh) )
			{
				rravg2 = 0;
				for (i = 0; i < 7; i++)
				{
					rr2[i] = rr2[i+1];
					rravg2 += rr2[i];
				}
				rr2[7] = rr1[7];
				rravg2 += rr2[7];
				rravg2 *= 0.125;
				rrlow = 0.92*rravg2;
				rrhigh = 1.16*rravg2;
				rrmiss = 1.66*rravg2;
			}

			prevRegular = regular;
			if (rravg1 == rravg2)
			{
				regular = true;
			}
			// If the beat had been normal but turned odd, change the thresholds.
			else
			{
				regular = false;
				if (prevRegular)
				{
					threshold_i1 /= 2;
					threshold_f1 /= 2;
				}
			}
		}
		// If no R-peak was detected, it's important to check how long it's been since the last detection.
		else
		{
		    // If no R-peak was detected for too long, use the lighter thresholds and do a back search.
			// However, the back search must respect the 200ms limit and the 360ms one (check the slope).
			if ((sample - lastQRS > (long unsigned int)rrmiss) && (sample > lastQRS + FS/5))
			{
				for (i = current - (sample - lastQRS) + FS/5; i < (long unsigned int)current; i++)
				{
					if ( (integral[i] > threshold_i2) && (highpass[i] > threshold_f2))
					{
					    currentSlope = 0;
                        for (j = i - 10; j <= i; j++)
                            if (squared[j] > currentSlope)
                                currentSlope = squared[j];

                        if ((currentSlope < (dataType)(lastSlope/2)) && (i + sample) < lastQRS + 0.36*lastQRS)
                        {
                            qrs = false;
                        }
                        else
                        {
                            peak_i = integral[i];
                            peak_f = highpass[i];
                            spk_i = 0.25*peak_i+ 0.75*spk_i;
                            spk_f = 0.25*peak_f + 0.75*spk_f;
                            threshold_i1 = npk_i + 0.25*(spk_i - npk_i);
                            threshold_i2 = 0.5*threshold_i1;
                            lastSlope = currentSlope;
                            threshold_f1 = npk_f + 0.25*(spk_f - npk_f);
                            threshold_f2 = 0.5*threshold_f1;
                            // If a signal peak was detected on the back search, the RR attributes must be updated.
                            // This is the same thing done when a peak is detected on the first try.
                            //RR Average 1
                            rravg1 = 0;
                            for (j = 0; j < 7; j++)
                            {
                                rr1[j] = rr1[j+1];
                                rravg1 += rr1[j];
                            }
                            rr1[7] = sample - (current - i) - lastQRS;
                            qrs = true;
                            lastQRS = sample - (current - i);
                            rravg1 += rr1[7];
                            rravg1 *= 0.125;

                            //RR Average 2
                            if ( (rr1[7] >= rrlow) && (rr1[7] <= rrhigh) )
                            {
                                rravg2 = 0;
                                for (i = 0; i < 7; i++)
                                {
                                    rr2[i] = rr2[i+1];
                                    rravg2 += rr2[i];
                                }
                                rr2[7] = rr1[7];
                                rravg2 += rr2[7];
                                rravg2 *= 0.125;
                                rrlow = 0.92*rravg2;
                                rrhigh = 1.16*rravg2;
                                rrmiss = 1.66*rravg2;
                            }

                            prevRegular = regular;
                            if (rravg1 == rravg2)
                            {
                                regular = true;
                            }
                            else
                            {
                                regular = false;
                                if (prevRegular)
                                {
                                    threshold_i1 /= 2;
                                    threshold_f1 /= 2;
                                }
                            }

                            break;
                        }
                    }
				}

				if (qrs)
                {
                    outputSignal[current] = false;
                    outputSignal[i] = true;
                    if (sample > DELAY + BUFFSIZE)
                        output(outputSignal[0]);
                    continue;
                }
			}

			// Definitely no signal peak was detected.
			if (!qrs)
			{
				// If some kind of peak had been detected, then it's certainly a noise peak. Thresholds must be updated accordinly.
				if ((integral[current] >= threshold_i1) || (highpass[current] >= threshold_f1))
				{
					peak_i = integral[current];
					npk_i = 0.125*peak_i + 0.875*npk_i;
					threshold_i1 = npk_i + 0.25*(spk_i - npk_i);
					threshold_i2 = 0.5*threshold_i1;
					peak_f = highpass[current];
					npk_f = 0.125*peak_f + 0.875*npk_f;
					threshold_f1 = npk_f + 0.25*(spk_f - npk_f);
					threshold_f2 = 0.5*threshold_f1;
				}
			}
		}
		// The current implementation outputs '0' for every sample where no peak was detected,
		// and '1' for every sample where a peak was detected. It should be changed to fit
		// the desired application.
		// The 'if' accounts for the delay introduced by the filters: we only start outputting after the delay.
		// However, it updates a few samples back from the buffer. The reason is that if we update the detection
		// for the current sample, we might miss a peak that could've been found later by backsearching using
		// lighter thresholds. The final waveform output does match the original signal, though.
		outputSignal[current] = qrs;
		if (sample > DELAY + BUFFSIZE)
			output(outputSignal[0]);